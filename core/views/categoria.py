from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.core.paginator import Paginator
from ..models import Categoria


def categoria_list(request):
    categorias = Categoria.objects.all().order_by('nombre')
    
    paginator = Paginator(categorias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'titulo': 'Categorías'
    }
    
    return render(request, 'core/categoria/list.html', context)


def categoria_create(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        
        if not nombre:
            messages.error(request, 'El nombre es obligatorio')
            return redirect('categoria_create')
        
        Categoria.objects.create(
            nombre=nombre,
            descripcion=descripcion
        )
        
        messages.success(request, 'Categoría creada correctamente')
        return redirect('categoria_list')
    
    context = {
        'titulo': 'Crear Categoría'
    }
    
    return render(request, 'core/categoria/form.html', context)


def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        
        if not nombre:
            messages.error(request, 'El nombre es obligatorio')
            return redirect('categoria_update', pk=pk)
        
        categoria.nombre = nombre
        categoria.descripcion = descripcion
        categoria.save()
        
        messages.success(request, 'Categoría actualizada correctamente')
        return redirect('categoria_list')
    
    context = {
        'categoria': categoria,
        'titulo': 'Editar Categoría'
    }
    
    return render(request, 'core/categoria/form.html', context)


def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        try:
            categoria.delete()
            messages.success(request, 'Categoría eliminada correctamente')
        except Exception as e:
            messages.error(request, f'No se puede eliminar esta categoría porque está siendo utilizada: {str(e)}')
        
        return redirect('categoria_list')
    
    context = {
        'categoria': categoria,
        'titulo': 'Eliminar Categoría'
    }
    
    return render(request, 'core/categoria/delete.html', context)
