from starlette_wtf import StarletteForm
from wtforms import TextField
from wtforms.validators import DataRequired, Length


class CreatePage(StarletteForm):
    name = TextField(
        "Community Name",
        validators=[
            DataRequired("Community name is required!"),
            Length(6, 32, "Name must be between 6 & 32!")
        ]
    )
