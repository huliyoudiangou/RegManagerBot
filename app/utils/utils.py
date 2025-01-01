from app.utils.logger import logger

# 需要安装的模块：无

def paginate_list(data_list, page_size):
    """
    对列表进行分页

    Args:
        data_list: 要分页的列表
        page_size: 每页的条目数

    Returns:
         一个列表的列表，其中每个内部列表代表一页数据
    """
    logger.debug(f"开始分页列表, pageSize={page_size}, listSize={len(data_list)}")
    if not data_list or page_size <= 0 :
        logger.warning("列表为空或者分页大小不合法")
        return []
    
    paginated_list = []
    # if len(data_list) <= page_size:
    #     paginated_list.append(data_list)
    #     logger.debug(f"无需分页")
    # else:
    for i in range(0, len(data_list), page_size):
        paginated_list.append(data_list[i:i + page_size])
    logger.debug(f"分页列表成功, 总页数={len(paginated_list)}, pageSize={page_size}, listSize={len(data_list)}")
    return paginated_list