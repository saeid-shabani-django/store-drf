from django.urls import path
from . import views
from rest_framework_nested import routers
router = routers.DefaultRouter()
router.register('products',views.ProductViewSet,basename='product')
router.register('categories',views.CategoryViewSet,basename='category')
product_router = routers.NestedDefaultRouter(router,'products',lookup='product')
product_router.register('comments',views.CommentViewSet,basename='product-comment')


router.register('carts',views.CartModelViewSet,basename='cart')
cart_items = routers.NestedDefaultRouter(router,'carts',lookup='cart')
cart_items.register('items',views.CartItemViewSet,basename='cart-items')


urlpatterns = router.urls + product_router.urls + cart_items.urls

# urlpatterns=[
#     path('products/',views.ProductList.as_view()),
#     path('products/<int:pk>/',views.ProductDetail.as_view()),
#     path('categories/',views.CategoryList.as_view()),
#     path('categories/<int:pk>/',views.CategoryDetail.as_view(),name='category_detail'),
# ]
