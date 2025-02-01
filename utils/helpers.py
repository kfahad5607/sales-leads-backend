def get_total_pages(total_count, page_size):
    return (total_count // page_size) + (1 if total_count % page_size else 0)