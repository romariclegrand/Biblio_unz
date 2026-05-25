from django.shortcuts import render
from django.views import View

class AProposView(View):
    def get(self, request):
        membres = [
            {'nom': 'Yelkouni Wend-nonga Romaric', 'role': 'Scrum Master', 'description': 'Chef de projet et développeur principal'},
            {'nom': 'Nabi Rachid', 'role': 'Développeur', 'description': 'Développement backend et base de données'},
            {'nom': 'Guelbeogo Saidou', 'role': 'Développeur', 'description': 'Développement frontend et interface utilisateur'},
            {'nom': 'Barry Roukietou', 'role': 'Développeur', 'description': 'Tests et qualité logicielle'},
            {'nom': 'Bassolé Judicael', 'role': 'Product Manager', 'description': 'Gestion des exigences et priorisation'},
            {'nom': 'Dr Moise Ouedraogo', 'role': 'Enseignant chercheur', 'description': 'Encadrement et supervision académique'},
        ]
        return render(request, 'core/apropos.html', {'membres': membres})
