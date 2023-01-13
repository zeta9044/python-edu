def print_lol(the_list):
    """중첩리스트의 값을 표시하는 함수"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
