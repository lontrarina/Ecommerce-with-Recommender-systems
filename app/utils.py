from .models import Product

# def get_similar_products(product, num=8):
#     """
#     Simple recommendation logic based on the same category.
#     Further improvement can be made by considering other attributes such as tags.
#     """
#     similar_products = Product.objects.all()
#     return similar_products[:num]


def get_similar_products(product):
    """
    Recommendation logic based on the 'styles' attribute containing the word 'office'.
    """
    similar_products = Product.objects.filter(styles__icontains='office').exclude(pk=product.pk)
    return similar_products