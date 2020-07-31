from SQLMatches import SQLMatches

import uvicorn


app = SQLMatches()

if __name__ == "__main__":
    uvicorn.run(app)
