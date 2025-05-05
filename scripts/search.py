# /// script
# dependencies = [
#   "httpx",
# ]
# ///

import json
import sys

import httpx

# --- Configuration ---
# TODO: EDIT THIS: The URL template where {} will be replaced by the integer
URL_TEMPLATE = "https://www.nytimes.com/svc/crosswords/v3/{}/stats-and-streaks.json?date_start=1988-01-01&start_on_monday=true"
# TODO: EDIT THIS: Maximum integer to search up to
MAX_INTEGER = 10_000_000_000  # 10 Billion
# TODO: EDIT THIS: How many integers to check downwards from the midpoint
N_CHECK_WINDOW = 1000
# TODO: EDIT THIS: Timeout for HTTP requests in seconds
REQUEST_TIMEOUT = 10
# --- End Configuration ---


def get_value_from_url(integer_value: int, client: httpx.Client) -> float | int | None:
    """
    Fetches data from the URL for the given integer and extracts the target value.

    Returns the numeric value if successful and non-zero, 0 if the value is zero
    or cannot be extracted/parsed, and None if there was a network/HTTP error.
    """
    url = URL_TEMPLATE.format(integer_value)
    try:
        response = client.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()

        # --- TODO: EDIT THIS Section ---
        # Replace this with the actual logic to extract the value from the JSON data.
        # Example: Accessing a nested key
        # Assume the JSON looks like: {"stats": {"items": {"count": 5}}}
        # target_value = data.get("stats", {}).get("items", {}).get("count", 0)

        # Example: Accessing a top-level key
        # Assume the JSON looks like: {"value": 123}
        target_value = data.get("results", {}).get("stats", {}).get("puzzles_solved", 0)

        # --- End EDIT Section ---

        # Ensure we handle non-numeric types gracefully, treating them as 0
        if not isinstance(target_value, (int, float)):
            print(
                f"Warning: Extracted value for {integer_value} is not numeric: {target_value}. Treating as 0.",
                file=sys.stderr,
            )
            return 0

        return target_value

    except httpx.HTTPStatusError as e:
        # If it's a 404 Not Found, we can often treat it as 'zero' for the search purpose
        if e.response.status_code == 404:
            print(
                f"Info: Received 404 Not Found for integer {integer_value}. Treating as 0.",
                file=sys.stderr,
            )
            return 0
        else:
            print(
                f"Warning: HTTP Error for integer {integer_value}: {e}", file=sys.stderr
            )
            return None  # Indicate a potentially transient error
    except httpx.RequestError as e:
        print(
            f"Warning: Network error for integer {integer_value}: {e}", file=sys.stderr
        )
        return None  # Indicate a potentially transient error
    except json.JSONDecodeError as e:
        print(
            f"Warning: Could not decode JSON for integer {integer_value}: {e}",
            file=sys.stderr,
        )
        return 0  # Treat invalid JSON as 0
    except KeyError as e:
        print(
            f"Warning: JSON key error for integer {integer_value}: {e}. Check JSON path. Treating as 0.",
            file=sys.stderr,
        )
        return 0  # Treat missing path as 0
    except Exception as e:
        # Catch other potential errors during extraction
        print(
            f"Warning: Unexpected error processing integer {integer_value}: {e}",
            file=sys.stderr,
        )
        return 0  # Treat other errors as 0


def check_integer_window(
    candidate_integer: int, client: httpx.Client, n_window: int
) -> bool:
    """
    Checks the candidate_integer and the N-1 integers below it.

    Returns True if any integer in the window [max(0, candidate_integer - n_window + 1), candidate_integer]
    has a non-zero value in the target JSON path. Returns False otherwise.
    Handles network errors by potentially retrying or skipping.
    """
    # Check from candidate_integer down to candidate_integer - n_window + 1
    # Ensure we don't go below zero
    start_check = candidate_integer
    end_check = max(0, candidate_integer - n_window + 1)

    print(f"Checking window: [{end_check}, {start_check}]")

    for i in range(start_check, end_check - 1, -1):
        value = get_value_from_url(i, client)

        if value is None:
            # Handle network/HTTP error - could retry, but for simplicity, we'll just skip
            # and hope other values in the window work or the binary search adjusts.
            # A more robust solution might retry here.
            print(f"Skipping check for {i} due to fetch error.", file=sys.stderr)
            # We might consider returning False immediately or after a few Nones,
            # but that could prematurely stop the search if the error is transient.
            # For now, continue checking others in the window.
            continue

        if value != 0:
            print(
                f"Found non-zero value ({value}) at integer {i} within window check for {candidate_integer}."
            )
            return True  # Found a non-zero value in the window

        # Optional: Add a small delay to avoid overwhelming the server
        # time.sleep(0.1)

    print(f"No non-zero value found in window [{end_check}, {start_check}].")
    return False  # No non-zero value found in the entire window


# --- Main Binary Search Logic ---
low = 0
high = MAX_INTEGER
best_found_integer = -1  # Initialize with a value indicating not found

# Use a context manager for the httpx client for efficient connection handling
with httpx.Client() as client:
    while low <= high:
        mid = low + (high - low) // 2  # Avoid potential overflow for very large numbers
        print("\n--- Iteration ---")
        print(f"Low: {low}, High: {high}, Mid: {mid}")

        # Perform the check on the window around 'mid'
        window_has_nonzero = check_integer_window(mid, client, N_CHECK_WINDOW)

        if window_has_nonzero:
            # If we found *something* non-zero in the window [mid-N+1, mid],
            # it means 'mid' is a potential candidate for being near the largest.
            # The actual largest could be 'mid' or higher.
            # Record this 'mid' as the best we've found *so far* that passed the check,
            # and try searching higher.
            best_found_integer = mid
            low = mid + 1
            print(
                f"Window check passed for {mid}. Possible max is >= {max(0, mid - N_CHECK_WINDOW + 1)}. Updating best_found={best_found_integer}, searching higher (low={low})."
            )
        else:
            # If the entire window [mid-N+1, mid] had zeros (or errors treated as zero),
            # it's likely the true largest integer is smaller than mid - N + 1.
            # So, we search in the lower half.
            high = mid - 1
            print(
                f"Window check failed for {mid}. True max is likely < {max(0, mid - N_CHECK_WINDOW + 1)}. Searching lower (high={high})."
            )

# --- Output Result ---
print("\n--- Search Finished ---")
if best_found_integer != -1:
    # Note: best_found_integer is the highest 'mid' for which the window check passed.
    # The *actual* largest integer with a non-zero value might be slightly lower
    # within the last successful window, but this 'mid' is our result from the search.
    # A final scan down from best_found_integer (up to N times) could pinpoint the exact one if needed.
    print("Binary search concluded.")
    print(
        f"The largest integer 'mid' for which the window check passed was: {best_found_integer}"
    )
    print(
        f"(The actual largest non-zero value is likely between [{max(0, best_found_integer - N_CHECK_WINDOW + 1)}, {best_found_integer}])"
    )

    # Optional: Final check to find the exact highest in the last successful window
    print(
        f"\nPerforming final scan down from {best_found_integer} to pinpoint exact value..."
    )
    exact_highest = -1
    for i in range(
        best_found_integer, max(0, best_found_integer - N_CHECK_WINDOW) - 1, -1
    ):
        value = get_value_from_url(i, client)
        if value is not None and value != 0:
            exact_highest = i
            print(
                f"Found exact highest non-zero value at {exact_highest} (value: {value})"
            )
            break
        # Add delay if needed
        # time.sleep(0.1)

    if exact_highest != -1:
        print(
            f"\nFinal Result: The estimated largest integer with a non-zero value is {exact_highest}"
        )
    else:
        print(
            f"\nFinal Result: Could not confirm exact highest in the final window scan down from {best_found_integer}."
        )
        print(f"Initial estimate based on search: {best_found_integer}")


else:
    print(
        "Binary search concluded. No integer found for which the window check passed."
    )
