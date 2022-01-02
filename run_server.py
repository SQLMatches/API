from SQLMatches import SQLMatches, DemoSettings, DatabaseSettings


app = SQLMatches(
    DemoSettings(),
    DatabaseSettings(
        username="...",
        password="...",
        database="sqlmatches"
    )
)


if __name__ == "__main__":
    app.serve()
