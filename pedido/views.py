from django.db.models.fields import CommaSeparatedIntegerField
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Pedido, ItemPedido, CupomDesconto
from produto.models import Produto, Categoria
import json

def finalizar_pedido(request):  
    if request.method == "GET":
        categorias = Categoria.objects.all()
        erro = request.GET.get('erro')
        total = sum([float(i['preco']) for i in request.session['carrinho']])
        return render(request, 'finalizar_pedido.html', {'carrinho': len(request.session['carrinho']),
                                                        'categorias': categorias,
                                                        'total': total,
                                                        'erro': erro})
    else:
        if len(request.session['carrinho']) > 0:
            x = request.POST
            total = sum([float(i['preco']) for i in request.session['carrinho']])
            cupom = CupomDesconto.objects.filter(codigo=x['cupom'])
            cupom_salvar = None
            if len(cupom) > 0 and cupom[0].ativo:
                total = total - ((total*cupom[0].desconto)/100)
                cupom[0].usos += 1
                cupom[0].save()
                cupom_salvar = cupom[0]

            carrinho = request.session.get('carrinho')
            listaCarrinho = []
            for i in carrinho:
                listaCarrinho.append({
                    'produto': Produto.objects.filter(id = i['id_produto'])[0],
                    'observacoes': i['observacoes'],
                    'preco': i['preco'],
                    'adicionais': i['adicionais'],
                    'quantidade': i['quantidade'],
                })
            

            lambda_func_troco = lambda x: int(x['troco_para'])-total if not x['troco_para'] == '' else ""
            lambda_func_pagamento = lambda x: 'Cartão' if x['meio_pagamento'] == '2' else 'Dinheiro'
            pedido = Pedido(usuario=x['nome'],
                            total = total,
                            troco = lambda_func_troco(x),
                            cupom = cupom_salvar,
                            pagamento = lambda_func_pagamento(x),
                            ponto_referencia = x['pt_referencia'],
                            cep = x['cep'],
                            rua = x['rua'],
                            numero = x['numero'],
                            bairro = x['bairro'],
                            telefone = x['telefone'],
                            )
            pedido.save()
            
            
            ItemPedido.objects.bulk_create(
                ItemPedido(
                    pedido = pedido,
                    produto = v['produto'],
                    quantidade = v['quantidade'],
                    preco = v['preco'],
                    adicionais = str(v['adicionais'])
                ) for v in listaCarrinho
            )
        
            request.session['carrinho'].clear()
            request.session.save()
            return render(request, 'pedido_realizado.html')
        else:
            return redirect('/pedidos/finalizar_pedido?erro=1')

def validaCupom(request):
    cupom = request.POST.get('cupom')
    cupom = CupomDesconto.objects.filter(codigo = cupom)
    if len(cupom) > 0 and cupom[0].ativo:
        desconto = cupom[0].desconto
        total = sum([float(i['preco']) for i in request.session['carrinho']])
        total_com_desconto = total - ((total*desconto)/100)
        data_json = json.dumps({'status': 0,
                                'desconto': desconto,
                                'total_com_desconto': str(total_com_desconto).replace('.', ',')

                                })
        return HttpResponse(data_json)
    else:
        return HttpResponse(json.dumps({'status': 1}))
