import json

class Dentists():
    def __init__(self, doctor = '', praxis='', item_type='', address='', telephone='', email='', website='', url=''):
        self.doctor = doctor  
        self.praxis = praxis
        self.item_type = item_type
        self.address = address
        self.telephone = telephone
        self.email = email
        self.website = website
        self.url = url

    def to_json(self):
        return json.dumps({'doctor': self.doctor,'praxis': self.praxis,'item_type': self.item_type,'address': self.address, 'telephone': self.telephone, 'email': self.email, 'website': self.website, 'url': self.url}, ensure_ascii=False)

    def __repr__(self):
        return (
            f"Dentists(doctor={repr(self.doctor)}, praxis={repr(self.praxis)}, "
            f"item_type={repr(self.item_type)}, address={repr(self.address)}, "
            f"telephone={repr(self.telephone)}, email={repr(self.email)}, "
            f"website={repr(self.website)}, url={repr(self.url)})"
        )