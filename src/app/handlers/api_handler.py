from mangum import Mangum

from app.api.main import app

# Create Mangum handler for AWS Lambda API Gateway integration
# This handles API Gateway event normalization and response formatting
handler = Mangum(app, lifespan="off")
