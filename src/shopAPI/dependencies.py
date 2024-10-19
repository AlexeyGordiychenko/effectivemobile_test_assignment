from uuid import UUID
from fastapi import Depends, HTTPException
from shopAPI.crud import OrderCRUD, ProductCRUD
from shopAPI.models import Order, OrderCreate, Product


async def valid_product_id(
    id: UUID,
    crud: ProductCRUD = Depends(),
) -> Product:
    product = await crud.get_by_id(id=id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {id} not found.")

    return product


async def valid_order_id(
    id: UUID,
    crud: OrderCRUD = Depends(),
) -> Order:
    order = await crud.get_by_id(id=id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {id} not found.")

    return order


async def valid_order_contents(
    data: OrderCreate,
    order_crud: OrderCRUD = Depends(),
    product_crud: ProductCRUD = Depends(),
) -> Order:
    order_items_ids: list[UUID] = [item.product_id for item in data.order_items]
    if len(order_items_ids) != len(set(order_items_ids)):
        raise HTTPException(
            status_code=400,
            detail="Duplicate product IDs.",
        )
    products: list[Product] = await product_crud.get_all_by_ids(ids=order_items_ids)
    products_dict: dict = {product.id: product for product in products}
    for item in data.order_items:
        product: Product = products_dict.get(item.product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found.",
            )
        elif product.amount < item.amount:
            raise HTTPException(
                status_code=400,
                detail=f"Product {product.id} not enough in stock.",
            )

    return await order_crud.create(data)
