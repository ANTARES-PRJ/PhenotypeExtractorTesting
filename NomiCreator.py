# ospedalimedici.py
# Liste di medici e ospedali con associazione uno a cinque

ospedali_medici = {
    "Holy Cross Hospital": ["Paolo Vitale", "Elena Marini", "Francesco De Angelis", "Giulia Neri", "Matteo Conti"],
    "Saint Michael Clinic": ["Laura Ferri", "Andrea Rinaldi", "Sofia Conti", "Luca Bianchi", "Valeria Russo"],
    "Saint Bartholomew Hospital": ["Giovanni Puglisi", "Chiara Romano", "Marco Fontana", "Federica Esposito", "Vincenzo Costa"],
    "Saint Teresa Polyclinic": ["Luca Moretti", "Giulia Galli", "Federico Ricci", "Sara Vitale", "Antonio Lombardi"],
    "Saint Anne Clinical Institute": ["Sara Colombo", "Alessandro Greco", "Federica Esposito", "Mario Ricci", "Elisa Ferrara"],
    "Saint Francis Hospital": ["Matteo Barbieri", "Valentina De Luca", "Stefano Marino", "Chiara Fontana", "Danilo Russo"],
    "Saint Lucy Hospital": ["Maria Rizzo", "Vincenzo Costa", "Anna Vitale", "Giorgio Ferri", "Francesca Puglisi"],
    "Bellavista General Hospital": ["Fabio Leone", "Elena Mancini", "Nicola Guerra", "Carlo Rinaldi", "Laura De Angelis"],
    "Saint Joseph Hospital of Valmontone": ["Carlo Rinaldi", "Francesca Perri", "Danilo Marchi", "Silvia Bianchi", "Leonardo Greco"],
    "Saint Lawrence Hospital of Modica": ["Antonio Russo", "Silvia Neri", "Luigi Ferrara", "Riccardo Marchi", "Martina Conti"],
    "Saint Benedict Polyclinic": ["Alessandra Greco", "Marco Galli", "Sofia Ricci", "Giovanni Lombardi", "Chiara Vitale"],
    "Saint Felix Hospital": ["Andrea De Rosa", "Carla Fontana", "Enrico Santoro", "Federico Leone", "Elena Marini"],
    "Novilia General Hospital": ["Giorgio Bianchi", "Martina Lombardi", "Salvatore Romano", "Maria Puglisi", "Matteo Galli"],
    "Saint Martin Hospital of Rivabella": ["Federico Marchetti", "Silvia De Luca", "Michele Conti", "Valentina Russo", "Luigi Esposito"],
    "Saint Charles Hospital of Alba": ["Carla Vitale", "Filippo Rizzi", "Elena Ferri", "Daniele Costa", "Paolo Moretti"],
    "Saint Paul Hospital of Altavilla": ["Leonardo Greco", "Riccardo Marchi", "Chiara Neri", "Alessandro Marino", "Laura Vitale"],
    "Molinetti Hospital of Rivoli": ["Paolo Galli", "Laura Marino", "Mario Fontana", "Francesco Leone", "Sara Rizzo"],
    "Cardarelli Hospital of Montesilvano": ["Valeria Ferrara", "Daniele Vitale", "Martina Rinaldi", "Antonio De Angelis", "Giulia Ricci"],
    "Saint Peter Hospital of Rimini": ["Vincenzo De Angelis", "Giorgio Leone", "Alessandra Ferri", "Stefano Puglisi", "Francesco Romano"],
    "Sun Queen Hospital": ["Chiara Puglisi", "Stefano Mancini", "Salvatore Marchi", "Elena Colombo", "Marco Vitale"],
}

# Stringhe con 50 nomi e 50 cognomi italiani
nomi_maschili_stringa = "Marco, Luca, Giovanni, Matteo, Francesco, Antonio, Alessandro, Stefano, Roberto, Giuseppe, Mario, Andrea, Davide, Fabio, Giorgio, Federico, Carlo, Luigi, Paolo, Riccardo, Vincenzo, Simone, Daniele, Nicola, Massimo, Enrico, Lorenzo, Claudio, Cristian, Giulio, Michele, Angelo, Salvatore, Pietro, Emanuele, Filippo, Gabriele, Alessio, Tommaso, Walter, Diego, Gianluca, Edoardo, Saverio, Cesare, Silvio, Dario, Giuliano, Tiziano, Armando"
nomi_femminili_stringa = "Giulia, Martina, Elisa, Francesca, Carla, Valeria, Silvia, Chiara, Federica, Elena, Anna, Alessandra, Caterina, Roberta, Ilaria, Laura, Loredana, Beatrice, Paola, Stefania, Rosa, Alessia, Gabriella, Maria, Teresa, Claudia, Serena, Arianna, Sabrina, Monica, Barbara, Daniela, Lucia, Tiziana, Antonella, Simona, Emma, Federica, Vittoria, Miriam, Margherita, Paola, Giulia, Camilla, Teresa, Marta"
cognomi_stringa = "Rossi, Russo, Ferrari, Esposito, Bianchi, Romano, Colombo, Ricci, Marino, Greco, Bruno, Gallo, Conti, De Luca, Costa, Giordano, Mancini, Rizzo, Lombardi, Moretti, Barbieri, Fontana, Santoro, Mariani, Rinaldi, Caruso, Ferrara, Gatti, Pugliese, Orlando, Amato, Leone, Sorrentino, Martinelli, Benedetti, Messina, Guerra, Palmieri, Longo, Serra, Farina, Parisi, Marchetti, Valentini, Pagano, Monti, Vitali, De Angelis, Fabbri, Pellegrini"

nomi_maschili_lista = nomi_maschili_stringa.split(", ")
nomi_femminili_lista = nomi_femminili_stringa.split(", ")
cognomi_lista = cognomi_stringa.split(", ")