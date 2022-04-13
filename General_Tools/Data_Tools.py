

def orderDictColum(colum_dict,raw_dict):
    result_dict = {}
    dict_1 = colum_dict
    dict_2 = raw_dict

    for key in dict_1.keys():
        if key not in dict_2.keys():
            result_dict[key] = dict_1[key]
        if key in dict_2.keys():
            if type(dict_1[key]) != type(dict_2[key]):
                y_type = type(dict_1[key])
                if dict_2[key] == None:
                    value = "0"
                else:
                    value = dict_2[key]
                result_dict[key] = y_type(value)
            else:
                result_dict[key] = dict_2[key]

    result = {}
    for key in dict_1.keys():
        result[key] = result_dict[key]
    return result
