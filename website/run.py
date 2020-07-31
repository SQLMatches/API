from SQLMatches import SQLMatches
from SQLMatches.settings import DatabaseSettings

import uvicorn


app = SQLMatches(
    DatabaseSettings(
        username="modulelift",
        password="Y2ZRSsje9qZHsxDu",
        server="localhost",
        port=3306,
        database="sqlmatches"
    )
)

if __name__ == "__main__":
    uvicorn.run(app)
