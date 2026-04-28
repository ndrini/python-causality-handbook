# 01 - Introduzione alla Causalità

## Riassunto

Il capitolo distingue tra **predizione** e **causalità**. Il machine learning è molto forte nel prevedere ciò che accadrà dato un certo pattern nei dati, ma le domande causali chiedono qualcosa di diverso: cosa succede se interveniamo e cambiamo qualcosa.

Per ragionare in modo causale si usa il linguaggio dei **risultati potenziali**. Per ogni unità `i` esistono due risultati possibili:

- `Y0i`: il risultato se l'unità non riceve il trattamento
- `Y1i`: il risultato se l'unità riceve il trattamento

Il trattamento è indicato con `Ti`:

- `Ti = 1` se l'unità è trattata
- `Ti = 0` altrimenti

Il punto cruciale è che **non possiamo osservare entrambi i risultati per la stessa unità**. Vediamo solo ciò che è successo davvero, mentre l'altro esito resta controfattuale. Questo è il **problema fondamentale dell'inferenza causale**.

L'effetto causale individuale sarebbe:

`Y1i - Y0i`

ma non è osservabile direttamente. Per questo si studiano effetti medi:

- **ATE**: effetto medio del trattamento su tutta la popolazione  
  `ATE = E[Y1 - Y0]`
- **ATT**: effetto medio del trattamento sui trattati  
  `ATT = E[Y1 - Y0 | T=1]`

Il capitolo mostra poi che la differenza tra media dei trattati e media dei non trattati **non è automaticamente un effetto causale**. Quella è solo un'associazione:

`E[Y | T=1] - E[Y | T=0]`

Questa associazione si scompone in:

`Associazione = ATT + Bias`

`E[Y|T=1] - E[Y|T=0] = E[Y1 - Y0 | T=1] + {E[Y0 | T=1] - E[Y0 | T=0]}`

Il termine finale è il **bias**. Misura quanto i trattati e i non trattati sarebbero stati diversi anche senza trattamento. Nell'esempio del capitolo, le scuole con tablet possono andare meglio non per i tablet, ma perché sono scuole più ricche e con più risorse.

Quindi, se i gruppi **non sono comparabili** prima del trattamento, l'associazione non è causalità. Se invece sono comparabili e differiscono solo per il trattamento, il bias scompare e la differenza tra medie può essere letta come effetto causale.

L'obiettivo dell'inferenza causale è quindi rendere trattati e controlli confrontabili, così da isolare il solo effetto del trattamento.

## Idee chiave

- Predizione e causalità non sono la stessa cosa.
- Le domande causali sono domande controfattuali: "cosa sarebbe successo se...?"
- Ogni unità ha due risultati potenziali: `Y0i` e `Y1i`.
- Possiamo osservare solo uno dei due risultati potenziali.
- L'effetto individuale `Y1i - Y0i` non è osservabile direttamente.
- Gli effetti medi principali sono `ATE` e `ATT`.
- La differenza tra medie osservate misura associazione, non necessariamente causalità.
- Il **bias** è la differenza preesistente tra trattati e non trattati.
- Fare inferenza causale significa eliminare o ridurre quel bias.

## Formula da ricordare

`E[Y|T=1] - E[Y|T=0] = ATT + Bias`

Se `E[Y0 | T=1] = E[Y0 | T=0]`, allora il bias è nullo e l'associazione coincide con l'effetto causale.

## In una frase

L'inferenza causale serve a capire se una differenza osservata è davvero prodotta dal trattamento oppure da differenze già presenti tra i gruppi.
