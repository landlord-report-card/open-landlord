from wtforms import Form, StringField, SelectField


class LandlordSearchForm(Form):
    choices = [
                ('Address', 'property_address'),
                ('Landlord Name', 'll_name'),
    select = SelectField('Search for landlord:', choices=choices)
    search = StringField('')