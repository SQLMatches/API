from SQLMatches import SQLMatches
from SQLMatches.settings import DatabaseSettings, B2UploadSettings

import uvicorn


app = SQLMatches(
    database_settings=DatabaseSettings(
        username="modulelift",
        password="Y2ZRSsje9qZHsxDu",
        server="localhost",
        port=3306,
        database="sqlmatches"
    ),
    upload_settings=B2UploadSettings(
        key_id="...",
        application_key="...",
        bucket_id="...",
        pathway="demos/",
        cdn_url="..."
    ),
    friendly_url="http://127.0.0.1:8000"
)


if __name__ == "__main__":
    uvicorn.run(app)
