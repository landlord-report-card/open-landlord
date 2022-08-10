from wtforms import Form, StringField, SelectField


class LandlordSearchForm(Form):
    choices = [
                ('property_address', 'Address'),
                ('ll_name', 'Landlord Name')
            ]
    select = SelectField('Search for landlord:', choices=choices)
    search = StringField('')