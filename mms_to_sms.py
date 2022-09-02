import xml.etree.ElementTree as ET

# convert MMS to SMS, as exported by SMS Backup and Restore for Android.
# the problem being solved is the fact that Google RCS messages were
# being exported as MMS, which Signal does not import.

class Sms:
    def __init__(self, address, date, out, body, sub_id, readable_date, contact_name):
        self.protocol = "0"
        self.address = address
        self.date = date
        self.type_ = "2" if out else "1"
        self.subject = "null"
        self.body = body
        self.toa = "null"
        self.sc_toa = "null"
        self.service_center = "null"
        self.read = "1"
        self.status = "-1"
        self.locked = "0"
        self.date_sent = "0"
        self.sub_id = sub_id
        self.readable_date = readable_date
        self.contact_name = contact_name

        self.el = self.build_element()

    def __str__(self):
        return str(self.el.attrib)

    def build_element(self):
        el = ET.Element("sms")
        el.attrib["protocol"] = self.protocol
        el.attrib["address"] = self.address
        el.attrib["date"] = self.date
        el.attrib["type"] = self.type_
        el.attrib["subject"] = self.subject
        el.attrib["body"] = self.body
        el.attrib["toa"] = self.toa
        el.attrib["sc_toa"] = self.sc_toa
        el.attrib["service_center"] = self.service_center
        el.attrib["read"] = self.read
        el.attrib["status"] = self.status
        el.attrib["locked"] = self.locked
        el.attrib["date_sent"] = self.date_sent
        el.attrib["sub_id"] = self.sub_id
        el.attrib["readable_date"] = self.readable_date
        el.attrib["contact_name"] = self.contact_name

        return el

def import_mms(root):
    smses = []

    for mms in root:
        date = mms.attrib["date"]
        address = mms.attrib["address"]
        sub_id = mms.attrib["sub_id"]
        readable_date = mms.attrib["readable_date"]
        contact_name = mms.attrib["contact_name"]

        part = mms[0][-1]
        body = part.attrib["text"]

        # out if address specified in head (contact) is not equal to sender.
        sender_address = mms[1][0].attrib["address"]
        out = address != sender_address

        sms = Sms(address, date, out, body, sub_id, readable_date, contact_name)
        smses.append(sms)

        #print(sms)

    return smses

def export_sms(smses):
    root = ET.Element("smses")

    for sms in smses:
        ET.SubElement(root, sms.el.tag, sms.el.attrib)

    tree = ET.ElementTree(root)
    tree.write("sms.xml", "UTF-8")

def main():
    tree = ET.parse('mms.xml')
    root = tree.getroot()

    smses = import_mms(root)
    export_sms(smses)

if __name__ == "__main__":
    main()
