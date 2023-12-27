import xmltodict

ATTACHMENTS_DIR = 'C:\\oncor\\attachments\\'


def get_diagnoses(attachment) -> list:

    def get_item_diagnoses(code197, code1076, code1077, diagnosis_date, item) -> set:
        print(f"code197={code197}, code1076={code1076}, code1077={code1077}, diagnosis_date={diagnosis_date}, item={item}")
        item_diagnoses = set()
        if isinstance(item, list):
            for it in item:
                item_diagnoses = item_diagnoses.union(
                    get_item_diagnoses(code197, code1076, code1077, diagnosis_date, it)
                )

        elif isinstance(item, dict):
            local_code1076 = code1076
            local_code1077 = code1077
            local_diagnosis_date = diagnosis_date
            item_code = item.get('code', None)
            if isinstance(item_code, dict):
                code_system = item_code.get('@codeSystem', '')
                if code_system == '1.2.643.5.1.13.13.11.1076' or code_system == '1.2.643.5.1.13.13.99.2.795':
                    local_code1076 = item_code.get('@code', local_code1076)
                if code_system == '1.2.643.5.1.13.13.11.1077':
                    local_code1077 = item_code.get('@code', local_code1077)
            item_effective_time = item.get('effectiveTime', None)
            if isinstance(item_effective_time, dict):
                local_effective_time = item_effective_time.get('@value', None)
                if isinstance(local_effective_time, str):
                    local_diagnosis_date = (
                        local_effective_time[0:4] + '-' +
                        local_effective_time[4:6] + '-' +
                        local_effective_time[6:8]
                    )
            code_system = item.get('@codeSystem', '')
            if code_system == '1.2.643.5.1.13.13.11.1005':
                print('Bingo!')
                local_mkb10 = item.get('@code', 'UNKNOWN')
                item_diagnoses = item_diagnoses.union(
                    {
                        (
                            local_mkb10,
                            local_diagnosis_date,
                            local_code1076,
                            local_code1077,
                            code197)
                    }
                )
            for it in item.keys():
                item_diagnoses = item_diagnoses.union(
                    get_item_diagnoses(code197, local_code1076, local_code1077, local_diagnosis_date, item[it])
                )

        print(f"item_diagnoses={item_diagnoses}")

        return item_diagnoses

    attachment_file = ATTACHMENTS_DIR + attachment[:2] + '\\' + attachment

    try:
        with open(attachment_file, 'r', encoding='utf-8') as f:
            xml_dict = f.read()
        xml_dict = xmltodict.parse(xml_dict)
    except Exception as e:
        print(f"{type(e)}: {str(e)}")
        return list()

    try:
        components = xml_dict['ClinicalDocument']['component']['structuredBody']['component']
        if not isinstance(components, list):
            return list()
    except Exception:
        return list()

    # Calculate diagnoses set
    diagnoses = set()

    for component in components:
        try:
            section = component['section']
            if not isinstance(section, dict):
                continue
        except Exception as e:
            print(f"{type(e)}: {str(e)}")
            continue

        code = section.get('code', None)
        if isinstance(code, dict):
            section_code197 = code.get('@code', None)
        else:
            section_code197 = None

        section_diagnoses = get_item_diagnoses(section_code197, None, None, None, section)

        print(section_diagnoses)

        diagnoses = diagnoses.union(section_diagnoses)

    # Save records to result
    result_diagnoses = list()
    for diagnosis in diagnoses:
        d = {'mkb10': diagnosis[0]}
        if diagnosis[1]:
            d['date'] = diagnosis[1]
        if diagnosis[2]:
            d['code1076'] = diagnosis[2]
        if diagnosis[3]:
            d['code1077'] = diagnosis[3]
        if diagnosis[4]:
            d['code197'] = diagnosis[4]
        result_diagnoses.append(d)

    return result_diagnoses


def run(*args):
    attachment = '550c8086b2787ad34df5b9491a67060025c687bb'
    diagnoses = get_diagnoses(attachment)
    print('----------------------------------------------------------------')
    print(diagnoses)
    print('----------------------------------------------------------------')
