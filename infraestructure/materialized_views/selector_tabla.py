from infraestructure.materialized_views import politico_query

class SelectorTabla:
    def __init__(self):
        pass

    category_to_view = {
        "politico": politico_query.create_deepfeel_materialized_view_politico,
        # agrega más categorías y funciones aquí
    }        

    def crear_view_por_categoria(self, table_name, analysis_id, category):
        funcion = self.category_to_view.get(category)

        if funcion:
            return funcion(analysis_id, table_name)
        else:
            raise ValueError(f"Categoría '{category}' no soportada")