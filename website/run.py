from SQLMatches import SQLMatches
from SQLMatches.settings import DatabaseSettings, B2Settings

import uvicorn


app = SQLMatches(
    DatabaseSettings(
        username="modulelift",
        password="Y2ZRSsje9qZHsxDu",
        server="localhost",
        port=3306,
        database="sqlmatches"
    ),
    B2Settings(
        key_id="...",
        application_key="..",
        bucket_id="...",
        pathway="demos/",
        cdn_url="..."
    ),
    friendly_url="http://127.0.0.1:8000"
)

if __name__ == "__main__":
    uvicorn.run(app)
