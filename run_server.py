from SQLMatches import SQLMatches, DemoSettings, DatabaseSettings


app = SQLMatches(
    DemoSettings(),
    DatabaseSettings(
        username="greg",
        password="b@Y6ah*955l&A5p$!B",
        database="sqlmatchesDb",
        server="localhost",
        port=3306
    )
)


if __name__ == "__main__":
    app.serve()
