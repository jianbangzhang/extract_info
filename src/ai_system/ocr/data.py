APPId = "2ec8923f"
APIKey = "70e7614c5841c7f9f20fa891be37f676"
APISecret = "MDViYzJkNmY2YTNmODUxOWU0OWQ0OGUy"



def get_request_data(zip_file_path,markdown_element_option,sed_element_option):
	"""
	:param zip_file_path:
	:param markdown_element_option:
	:param sed_element_option:
	:return:
	"""
	request_data = {
		"header":{
			"app_id":"123456",
			"uid":"39769795890",
			"did":"SR082321940000200",
			"imei":"8664020318693660",
			"imsi":"4600264952729100",
			"mac":"6c:92:bf:65:c6:14",
			"net_type":"wifi",
			"net_isp":"CMCC",
			"status":0,
			"res_id":""
		},
		"parameter":{
			"ocr":{
				"result_option":"normal",
				"result_format":"json,markdown",
				"output_type":"one_shot",
				"exif_option":"0",
				"json_element_option":"",
				"markdown_element_option":markdown_element_option,
				"sed_element_option":sed_element_option,
				"alpha_option":"0",
				"rotation_min_angle":5,
				"result":{
					"encoding":"utf8",
					"compress":"raw",
					"format":"plain"
				}
			}
		},
		"payload":{
			"image":{
				"encoding":"jpg",
				"image":zip_file_path,
				"status":0,
				"seq":0
			}
		}
	}
	return request_data




response_path_list = ['$..payload.result', ]