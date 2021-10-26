from django.contrib import admin
from .models import ItemPedido, Pedido, CupomDesconto
from django.http import HttpResponse


@admin.register(CupomDesconto)
class CupomDescontoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'desconto', 'ativo')
    readonly_fields=('usos',)

class itemPedidoInline(admin.TabularInline):
    readonly_fields = ('produto', 'quantidade', 'preco', 'descricao', 'adicionais',)
    model = ItemPedido
    extra = 1


class PedidoAdmin(admin.ModelAdmin):
    inlines = [
        itemPedidoInline
    ]
    list_display = ('usuario', 'total', 'data', 'entregue')
    search_fields = ('entregue',)
    readonly_fields = ('usuario', 'total', 'troco', 'pagamento', 'ponto_referencia', 'data', 'cep', 'rua', 'numero', 'bairro', 'telefone')
    list_filter = ('entregue',)
admin.site.register(Pedido, PedidoAdmin)