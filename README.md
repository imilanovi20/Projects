# Višeagentni sustav za predikciju rezultata nogometnih utakmica

Implementiran je sustav za predikciju rezultata nogometnih utakmica koristeći specjalizirane agente za pojedine zadatke.

Sustav radi na način tako da korisnik odabere raspon datuma, nakon toga agent za dohvaćanje budućih utakmica dohvati sve utakmice u zadanome razdoblju koje će se održati te šalje jednu po jednu utakmicu agentu za dohvaćanje potrebnih metrika. Nakon što se dohvate sve potrebne metrike za pojedinu utakmicu agent šalje podatke agentu za predikciju rezultata. Nakon što agent za predikciju napravi potrebno šalje prethodnom agentu da je predikcija napravljena te agent za dohvaćanje metrika šalje tu istu poruku agentu za dohvaćanje utakmica. U tom trenutku agent za dohvaćanje utakmica šalje slijedeću utakmicu agentu za dohvaćanje metrika i tako u krug.

Primjer rada sustava nalazi se u nastavku.

![pocetna](https://github.com/user-attachments/assets/d247c4ad-2c25-47b5-a194-e395684ee8e9)

![rezultati](https://github.com/user-attachments/assets/ea657cf1-40f8-48cb-bbc1-76d2727fe066)



## Korišteni podatci

Za predikciju rezultata korišten je Random Forest algoritam. Za učenje sustava korišteni su podatci sa platforme Kaggle. Podatci su preuzeti sa platforme i spremljeni u *data/train_model* uz pomoć python skripte iz orginalnog csv-a su filtrirani samo pojedni atributi koji će se koristiti za predikcije a to su:

+ team_a_ppg_dif_l4: Razlika u broju bodova po utakmici za tim A u posljednje četiri
utakmice.
+ team_b_ppg_dif_l4: Razlika u broju bodova po utakmici za tim B u posljednje četiri
utakmice.
+ team_a_shots_average: Prosječan broj šutova za tim A.
+ team_b_shots_average: Prosječan broj šutova za tim B.
+ predict_xg_overall_team_a: Predviđeni ukupni očekivani golovi za tim A.
+ predict_xg_overall_team_b: Predviđeni ukupni očekivani golovi za tim B.
+ position_a_prematch: Pozicija tima A na tablici prije utakmice.
+ position_b_prematch: Pozicija tima B na tablici prije utakmice.
+ predict_xg_home_team_a: Predviđeni očekivani golovi za tim A kod kuće.
+ predict_xg_away_team_b: Predviđeni očekivani golovi za tim B u gostima.

Kako bi se omogućila predikcija konačnog rezultata utakmice, u podatke je uvedena i
nova ciljana varijabla Results. Ova varijabla definirana je na sljedeći način:
+ Ako je domaći tim (Home team) pobijedio, Results je postavljen na 0.
+ Ako je gostuju´ci tim (Away team) pobijedio, Results je postavljen na 1.
+ Ako je rezultat bio neriješen (Draw), Results je postavljen na 2.

### Dohvaćanje podataka za buduće utakmice

Za dohvat informacija o svim utakmicama u tekućoj sezoni, odlučeno je koristiti API platforme football-data.org. Kreiran je API ključ te su uz pomoć python skripte dohvaćeni svi podatci o tekučoj sezoni te su spremljni u *data*. Iz spremljenih podataka uz pomoć agenata dohvaćaju se podatci o budućim utakmicama, ali i posljednjim odigranim utakmicama, odnosno rezultatima u posljednje 4 utakmice za pojedini tim. 

Za analizu očekivanih golova (xG) i trenutne pozicije timova na tablici koristi se platforma Understat na adresi: understat.com. Podatci su izravno preuzei sa platforme i spremljeni u *data*.

Podaci o prosječnom broju šutova timova preuzeti su sa stranice FBref na adresi: fbref.com. Podatci su izravno preuzei sa platforme i spremljeni u *data*.

## Agenti

Sustav se sastoji od 3 agenta: GetMatchesAgent, GetMatchesDataAgent, i RandomForestAgent.

## Pokretanje sustava

Sustav radi unutar Conda virtualnog okruženja koje se koristi za komunukaciju među agentima. Potrebnu je instalirati pokrenuti okruženje kako bi kod radio.

Dodatne bibliteke:
pip install pandas scikit-learn

Da bi se kod pokrenio potrebno je prethodno instalirati sve potrebne biblioteke
Postoje 2 načina pokretanja

1. python3 main.py
   + ako se želi samo ispis u konzoli i generiranje JSON datoteka iz kojeg se čitaju predikcije
2. python3 app.py
   + ako se želi pokrenuti web sučelje
   + odabere se početni i završni datum i čeka se 30 sekundi nakon čega se prikazuju predikcije
   
