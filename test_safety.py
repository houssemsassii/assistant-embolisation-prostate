"""
Script de test des fonctionnalités de sécurité du chatbot médical.
Vérifie que le système refuse correctement les données personnelles.

Usage: python test_safety.py
"""

import sys
from pathlib import Path

# Import des fonctions de sécurité depuis app.py
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app import detect_personal_data
except ImportError:
    print("❌ Erreur: Impossible d'importer app.py")
    print("   Assurez-vous que app.py existe dans le même dossier.")
    sys.exit(1)


# ============================================
# TESTS DE DÉTECTION DE DONNÉES PERSONNELLES
# ============================================

TESTS_QUESTIONS = [
    # Questions qui DOIVENT être détectées comme personnelles
    {
        "question": "J'ai 70 ans, puis-je faire cette opération ?",
        "should_detect": True,
        "reason": "Âge personnel"
    },
    {
        "question": "Je prends du Kardegic, dois-je l'arrêter ?",
        "should_detect": True,
        "reason": "Traitement personnel"
    },
    {
        "question": "Dans mon cas, quels sont les risques ?",
        "should_detect": True,
        "reason": "Situation personnelle"
    },
    {
        "question": "Mon médecin m'a dit que j'avais un PSA élevé",
        "should_detect": True,
        "reason": "Information médicale personnelle"
    },
    {
        "question": "Mes résultats d'IRM montrent une prostate de 80g",
        "should_detect": True,
        "reason": "Résultats d'examens"
    },
    {
        "question": "Suis-je à risque de complications ?",
        "should_detect": True,
        "reason": "Évaluation de risque personnel"
    },
    {
        "question": "Est-ce grave dans ma situation ?",
        "should_detect": True,
        "reason": "Situation personnelle"
    },
    {
        "question": "Je suis diabétique, y a-t-il des précautions ?",
        "should_detect": True,
        "reason": "Condition médicale personnelle"
    },
    
    # Questions qui NE DOIVENT PAS être détectées (questions générales valides)
    {
        "question": "Qu'est-ce que l'embolisation de la prostate ?",
        "should_detect": False,
        "reason": "Question générale"
    },
    {
        "question": "Quels sont les effets secondaires courants ?",
        "should_detect": False,
        "reason": "Question générale"
    },
    {
        "question": "Combien de temps dure l'hospitalisation ?",
        "should_detect": False,
        "reason": "Question générale"
    },
    {
        "question": "Quelles sont les contre-indications générales ?",
        "should_detect": False,
        "reason": "Question générale"
    },
    {
        "question": "Comment se déroule la procédure ?",
        "should_detect": False,
        "reason": "Question générale"
    },
    {
        "question": "Quels examens sont nécessaires avant ?",
        "should_detect": False,
        "reason": "Question générale"
    },
]


def run_tests():
    """
    Exécute les tests de sécurité.
    """
    print("=" * 70)
    print("🧪 TESTS DE SÉCURITÉ - DÉTECTION DE DONNÉES PERSONNELLES")
    print("=" * 70)
    print()
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(TESTS_QUESTIONS, 1):
        question = test["question"]
        should_detect = test["should_detect"]
        reason = test["reason"]
        
        # Exécution du test
        detected = detect_personal_data(question)
        
        # Vérification du résultat
        success = (detected == should_detect)
        
        if success:
            passed += 1
            status = "✅ PASS"
            color = "\033[92m"  # Vert
        else:
            failed += 1
            status = "❌ FAIL"
            color = "\033[91m"  # Rouge
        
        reset_color = "\033[0m"
        
        print(f"{color}{status}{reset_color} Test #{i}")
        print(f"   Question: \"{question}\"")
        print(f"   Attendu: {'REFUSÉE' if should_detect else 'ACCEPTÉE'} ({reason})")
        print(f"   Résultat: {'REFUSÉE' if detected else 'ACCEPTÉE'}")
        
        if not success:
            print(f"   ⚠️  Comportement inattendu!")
        
        print()
    
    # Résumé
    print("=" * 70)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 70)
    print(f"Tests réussis:  {passed}/{len(TESTS_QUESTIONS)}")
    print(f"Tests échoués:  {failed}/{len(TESTS_QUESTIONS)}")
    print(f"Taux de succès: {passed / len(TESTS_QUESTIONS) * 100:.1f}%")
    print()
    
    if failed == 0:
        print("✅ Tous les tests sont passés ! Le système de sécurité fonctionne correctement.")
        return 0
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les patterns de détection dans app.py")
        print("   Variable à ajuster: PERSONAL_DATA_KEYWORDS")
        return 1


def print_detected_patterns():
    """
    Affiche les patterns de détection configurés.
    """
    from app import PERSONAL_DATA_KEYWORDS
    
    print("\n" + "=" * 70)
    print("🔍 PATTERNS DE DÉTECTION ACTUELS")
    print("=" * 70)
    print()
    
    for i, pattern in enumerate(PERSONAL_DATA_KEYWORDS, 1):
        print(f"{i}. {pattern}")
    
    print()


def main():
    """
    Point d'entrée principal.
    """
    print()
    
    # Affichage des patterns
    print_detected_patterns()
    
    # Exécution des tests
    exit_code = run_tests()
    
    # Recommandations
    print("💡 RECOMMANDATIONS:")
    print("   - Ajustez PERSONAL_DATA_KEYWORDS dans app.py si nécessaire")
    print("   - Testez avec de vraies questions de patients")
    print("   - Documentez les cas limites rencontrés")
    print()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
