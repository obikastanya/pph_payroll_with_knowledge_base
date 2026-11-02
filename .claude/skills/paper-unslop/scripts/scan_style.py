"""Style scanner for AI-text patterns in a paper (LaTeX or plain text, Indonesian or English).

    python scan_style.py paper.tex [--summary] [--rules K6,P6] [--synonyms "knowledge base|KB|basis pengetahuan"]

Prints findings per paragraph with the line number and the rule id from SKILL.md, then sentence and paragraph
statistics. The scanner is a first filter: every finding is judged by hand, and patterns that need reading
(P3, P12, P21, W1, W4-W10, W12, W13, W16, F7-F10) are only partly detected or not at all.
--synonyms takes groups of terms for one concept (groups separated by ';', terms by '|'); a paragraph that uses
two terms of one group is reported under B5.
"""
import argparse
import re
import statistics
import sys
from collections import Counter

# ---------------------------------------------------------------------------------------------------------------
# Word lists (rule id -> patterns). Patterns are lower-case regular expressions matched on word boundaries.
# ---------------------------------------------------------------------------------------------------------------
VOCAB = {
    "B1": [
        r"delv\w*", r"intricate", r"pivotal", r"underscor\w*", r"showcas\w*", r"leverag\w*", r"seamless\w*",
        r"robust\w*", r"comprehensive", r"meticulous\w*", r"commendable", r"notably", r"multifaceted", r"paramount",
        r"landscape", r"realm", r"tapestry", r"testament", r"harness\w*", r"unlock\w*", r"elevat\w*", r"crucial",
        r"enhanc\w*", r"foster\w*", r"garner\w*", r"interplay", r"vibrant", r"enduring", r"shed\w* light",
        r"pave\w* the way", r"cutting-edge", r"groundbreaking", r"game-changer", r"worth noting", r"novel",
        r"holistic", r"nuanced", r"emerged as", r"navigat\w* the complexit\w*", r"ever-evolving",
        r"plays? an? (key|vital|central|important|pivotal) role", r"it is evident", r"a wide (range|array|variety) of",
        r"a growing body of", r"in recent years", r"gained traction", r"bridg\w* the gap",
        r"memainkan peran", r"memegang peran(an)?", r"(ber)?peran(an)? (yang )?(krusial|penting|kunci|sentral|vital)",
        r"krusial", r"menyoroti", r"(meng|di)garisbawahi", r"menegaskan pentingnya", r"lanskap", r"ranah",
        r"komprehensif", r"holistik", r"wawasan (yang )?(berharga|mendalam)",
        r"kontribusi (yang )?(berarti|signifikan|nyata|besar)", r"membuka jalan", r"menjadi landasan", r"inovatif",
        r"mutakhir", r"revolusioner", r"canggih", r"sangat efektif", r"sangat efisien", r"era digital",
        r"seiring (dengan )?perkembangan", r"perlu dicatat", r"penting untuk (dicatat|diketahui|dipahami)",
        r"perlu diketahui", r"(me|di)manfaatkan", r"(meng|di)optimalkan", r"mulus", r"tangguh", r"andal",
        r"dalam beberapa (tahun|dekade) terakhir", r"semakin (banyak|meningkat|populer|penting|kompleks)",
        r"mendapat(kan)? perhatian", r"menarik perhatian", r"menjawab tantangan", r"tantangan (besar|utama)",
        r"solusi (yang )?(efektif|tepat|inovatif)", r"dewasa ini", r"tidak terlepas dari", r"tak terpisahkan",
        r"pemangku kepentingan", r"implikasi (yang )?(penting|luas|besar)",
        r"insights? into", r"exhibit\w*", r"emphasiz\w*", r"invaluable", r"unprecedented", r"noteworthy",
        r"unveil\w*", r"embark\w*", r"intricacies",
    ],
    # archaic, literary or showy words with a plain equivalent (SKILL.md table B7)
    "B7": [
        r"tatkala", r"manakala", r"bilamana", r"niscaya", r"senantiasa", r"acap ?kali", r"kerap( kali)?",
        r"termaktub", r"ihwal", r"kiranya", r"hendaknya", r"notabene", r"mumpuni", r"gamblang", r"esensial",
        r"esensi", r"signifikansi", r"optimalisasi", r"sinergi\w*", r"akselerasi", r"eskalasi", r"elaborasi",
        r"implementatif", r"aplikatif", r"transformatif", r"urgensi", r"determinan", r"masif", r"diskursus",
        r"eksistensi", r"konstelasi", r"akomodatif", r"dinamika", r"nirkabel", r"teraktualisasi", r"terejawantah\w*",
        r"mengejawantahkan", r"pengejawantahan", r"paripurna", r"mutlak", r"adiluhung",
        r"myriad", r"plethora", r"endeavou?r\w*", r"commenc\w*", r"aforementioned", r"henceforth", r"thereby",
        r"wherein", r"whereby", r"albeit", r"notwithstanding", r"elucidat\w*", r"salient", r"bolster\w*",
        r"spearhead\w*", r"underpin\w*", r"streamlin\w*", r"encompass\w*", r"culminat\w*", r"juxtapos\w*",
        r"exemplif\w*", r"burgeoning", r"quintessential", r"profound\w*", r"unwavering", r"ascertain\w*",
    ],
    # certainty boosters: as formulaic as stacked hedges (K9)
    "K9": [r"tidak diragukan lagi", r"tak pelak( lagi)?", r"sudah pasti", r"(sudah )?jelas bahwa", r"tentunya",
           r"pastinya", r"sudah barang tentu", r"undoubtedly", r"clearly", r"obviously", r"of course",
           r"it is clear that", r"without (a )?doubt", r"indisputabl\w*", r"unquestionabl\w*"],
    "B2": [r"serves? as", r"stands? as", r"boasts?", r"berperan sebagai", r"bertindak sebagai", r"hadir sebagai",
           r"berfungsi sebagai", r"menjadi kunci", r"menawarkan", r"(functions?|operates?) as an?",
           r"offers? (a|an) (unique|comprehensive|powerful|robust|novel|promising|valuable|rich|wide|flexible|"
           r"principled|practical|scalable)"],
    # English: significance inflation (E1)
    "E1": [r"a testament to", r"reflects? (a )?broader", r"setting the stage for", r"sets? the stage for",
           r"marks? (a|an) (shift|turning point|milestone|departure|step change)", r"(key|pivotal) turning point",
           r"focal point", r"indelible", r"deeply rooted", r"evolving landscape", r"pivotal moment",
           r"underscor\w* the (importance|need|value|potential)", r"highlight\w* the (importance|need|value|potential)",
           r"is of (paramount|utmost|critical) importance", r"cannot be overstated", r"lies at the heart of",
           r"at the forefront of", r"in the (era|age) of", r"in today's", r"rapidly evolving", r"ever-changing",
           r"serves? a (dual|twofold|double) purpose", r"reflects? a (deliberate|conscious|careful) (trade-off|choice)",
           r"paints? a (clear|compelling|vivid|nuanced) picture", r"compelling",
           r"poses? (a )?(significant|serious|major) (challenges?|risks?|threats?)", r"we envision a future",
           r"will play an increasingly \w+ role", r"keeps? pace with", r"a (new|next) generation of",
           r"a diverse (range|array|set) of", r"(special|great|particular) care was taken",
           r"the single most (important|critical|effective)"],
    # English: soft AI vocabulary of 2024-2026 models, reported only when two distinct items meet in a paragraph (E2)
    "E2": [r"additionally", r"align\w* (well |closely )?with", r"resonat\w* with", r"highlight(s|ed|ing)?",
           r"valuable", r"key (insight|challenge|contribution|factor|component|finding|takeaway|aspect|driver)s?",
           r"deep dive", r"lever", r"pays? off", r"where it matters( most)?", r"clearer", r"dependable", r"echo(es|ed)", r"matters", r"practical", r"prioriti[sz]\w*",
           r"quietly", r"steady", r"universally", r"crucially", r"ultimately", r"meaningful(ly)?", r"tailored",
           r"actionable", r"empower\w*", r"streamlined"],
    # English and Indonesian: formulaic research moves (E6)
    "E6": [r"to address (this|these|the|such) (gap|challenge|issue|limitation|problem|shortcoming)s?",
           r"to this end", r"in this regard", r"in light of (this|these)", r"with this in mind",
           r"against this backdrop", r"building (up)?on (this|these|prior|previous|recent)", r"(in|by) doing so",
           r"our (main |key )?contributions are (as follows|threefold|twofold|summarized)",
           r"the remainder of (this|the) (paper|article) is (organized|structured)",
           r"extensive experiments (demonstrate|show|confirm)",
           r"demonstrat\w* the (effectiveness|efficacy|superiority|robustness|feasibility)",
           r"state-of-the-art performance", r"opens? (up )?(new|exciting) avenues", r"a promising (direction|avenue)",
           r"future (work|research) (could|can|will|should) (explore|investigate)",
           r"untuk mengatasi (masalah|permasalahan|tantangan|keterbatasan) (ini|tersebut)",
           r"menunjukkan efektivitas", r"membuka peluang"],
    # English: informal register and contractions (E7)
    "E7": [r"it's", r"don't", r"doesn't", r"can't", r"won't", r"isn't", r"aren't", r"wasn't", r"weren't", r"we're",
           r"they're", r"that's", r"there's", r"a lot of", r"lots of", r"huge", r"really", r"pretty (good|much|well)",
           r"kind of", r"sort of", r"basically", r"literally", r"super"],
    "B3": [r"substrate", r"locus", r"nexus", r"paradigm\w*", r"modalit\w*", r"scaffold\w*", r"north star",
           r"flywheel", r"bedrock", r"fondasi", r"pilar", r"tulang punggung", r"jantung dari", r"payung"],
    "B4": [r"utiliz\w*", r"facilitat\w*", r"numerous", r"in the event that", r"mengutilisasi", r"utilisasi",
           r"memfasilitasi", r"guna", r"dalam rangka", r"terkait dengan", r"adapun", r"yang mana", r"di mana",
           r"dimana", r"bertujuan untuk", r"adalah merupakan", r"in the context of", r"with respect to",
           r"dengan menggunakan"],
    "B6": [r"berbagai", r"beragam", r"sejumlah", r"various", r"a variety of"],
    "K8": [r"sangat", r"amat", r"jauh lebih", r"benar-benar", r"substantially", r"greatly", r"very",
           r"dramatically", r"luar biasa", r"menjanjikan", r"memuaskan", r"(performa|kinerja|akurasi|hasil) "
           r"(yang )?(baik|tinggi|optimal|unggul|memuaskan)", r"remarkabl\w*", r"promising", r"impressive",
           r"valuable insights?", r"excellent", r"superior performance", r"strong performance"],
    "P19": [r"perlu dicatat", r"penting untuk diketahui", r"dapat dikatakan", r"pada dasarnya", r"dalam hal ini",
            r"(sebagaimana|seperti)( yang)?( kita)? (di)?ketahui", r"in order to", r"due to the fact",
            r"it is important to note", r"it should be (emphasized|stressed|highlighted|mentioned)",
            r"dapat dilihat bahwa", r"terlihat bahwa", r"dapat disimpulkan bahwa",
            r"tidak dapat dipungkiri", r"perlu ditekankan", r"it can be seen that", r"it should be noted",
            r"adalah penting untuk", r"merupakan hal yang", r"hal yang (sangat )?(penting|krusial|esensial|vital)",
            r"it is worth (mentioning|highlighting|emphasizing|pointing out)", r"based on (the )?available information",
            r"while specific details are (limited|scarce)", r"the fact that", r"needless to say",
            r"it goes without saying"],
    "P20": [r"secara (otomatis|efektif|efisien|eksplisit|signifikan|substansial|drastis|menyeluruh|mendalam|optimal|"
            r"berkelanjutan|cermat|luas|mendasar|komprehensif|sistematis|holistik)"],
    "P21": [r"menavigasi", r"menjembatani (kesenjangan|celah)", r"benang merah"],
    "P27": [r"efektif dan efisien", r"jelas dan terorganisir", r"cepat dan tepat", r"akurat dan andal",
            r"baik secara \w+ maupun( secara)? \w+", r"teoretis maupun praktis", r"aman dan nyaman",
            r"efficient and effective", r"accurate and reliable", r"clear and concise"],
    "W14": [r"diharapkan (dapat|mampu|bisa|akan)", r"dengan adanya [^.]{1,60}diharapkan", r"hopefully",
            r"is expected to (contribute|provide|help)"],
    "W15": [r"masih (sangat )?(terbatas|jarang)", r"belum banyak (penelitian|studi|kajian)", r"celah penelitian",
            r"kesenjangan penelitian", r"remains? (largely )?(unexplored|underexplored|limited)",
            r"research gap", r"little attention", r"underexplored",
            r"despite (the )?(growing|increasing|recent|rapid) (interest|attention|advances|progress)",
            r"(existing|prior|previous) (work|research|studies|approaches|methods) (has|have) (largely|mainly|"
            r"primarily|mostly) (focused|relied|concentrated)", r"leaving [^.]{0,60}(unexplored|underexplored|"
            r"unaddressed|open)", r"has received (little|limited|scant) attention"],
    # cliché limitation and future-work moves (F10)
    "F10": [r"(several|some|a few) limitations (should|must|need to) be (acknowledged|noted|considered)",
            r"beyond the scope of (this|the present|the current) (study|paper|work)",
            r"while (our|these|the) results are (encouraging|promising)", r"future (work|research) (could|can|will|"
            r"should|may) (explore|investigate|extend|address)", r"larger (and more diverse )?datasets?",
            r"penelitian (selanjutnya|berikutnya|mendatang) (dapat|diharapkan|disarankan)",
            r"keterbatasan (dalam )?penelitian ini"],
    # textbook definitions and over-explaining (W16)
    "W16": [r"in simple terms", r"refers to the process (by|through) which", r"the mechanism (by|through) which",
            r"is defined as the process", r"secara sederhana", r"merupakan suatu proses", r"adalah suatu proses",
            r"dapat diartikan sebagai", r"didefinisikan sebagai suatu"],
    "F13": [r"(telah )?berhasil (mengembangkan|membangun|membuktikan|menunjukkan|meningkatkan)", r"terbukti (mampu|efektif|andal|berhasil)",
            r"membuktikan bahwa", r"tujuan penelitian (ini )?(telah )?tercapai", r"successfully (developed|demonstrated|achieved)",
            r"proves? that", r"our (results|findings|experiments) (demonstrate|confirm|prove)",
            r"(clearly|convincingly) (demonstrates?|shows?)"],
    # Indonesian-to-English translationese (E9)
    "E9": [r"has experienced (several |many |a )?(changes?|increases?|decreases?|improvements?)",
            r"in the last years", r"number \d+ year \d{4}", r"which is valid since", r"(is|was|are|were) done by",
            r"from [\d.,]+ \w* ?become", r"it can be concluded that", r"based on the (results|research|explanation) "
            r"(of|above)", r"(is|are) able to answer", r"problem formulation", r"this research (is|aims|shows|uses)",
            r"has been (stated|explained|mentioned) (in|before|above)", r"the newest", r"in this case,",
            r"the calculation result"],
    "F6": [r"certainly", r"as an ai", r"insert citation", r"citation needed", r"knowledge cutoff", r"berikut adalah",
           r"semoga membantu", r"todo", r"tentu saja!", r"mari kita", r"bayangkan", r"let us", r"let's"],
}
TRANSITIONS = [
    "namun", "akan tetapi", "tetapi", "selain itu", "lebih lanjut", "lebih jauh", "dengan demikian", "oleh karena itu",
    "oleh sebab itu", "karena itu", "maka dari itu", "maka", "akibatnya", "sementara itu", "di sisi lain", "sebaliknya",
    "padahal", "meskipun demikian", "walaupun demikian", "namun demikian", "kendati demikian", "tidak hanya itu",
    "lebih dari itu", "lebih penting lagi", "tidak kalah penting", "terlebih lagi", "bahkan", "adapun", "kemudian",
    "lalu", "selanjutnya", "berikutnya", "pertama-tama", "pertama", "kedua", "ketiga", "keempat", "terakhir",
    "sebagai contoh", "sebagai ilustrasi", "dengan kata lain", "secara umum", "secara khusus", "secara keseluruhan",
    "pada dasarnya", "dalam hal ini", "untuk itu", "singkatnya", "intinya", "jadi", "ke depannya", "ke depan",
    "sebagaimana diketahui", "menariknya", "ironisnya", "uniknya", "tentunya", "tentu saja", "jelas", "faktanya",
    "nyatanya", "sejatinya", "idealnya", "sayangnya", "untungnya", "pada akhirnya", "alhasil", "hasilnya",
    "yang menarik", "however", "moreover", "furthermore", "additionally", "therefore", "thus", "hence",
    "in addition", "in contrast", "consequently", "first", "second", "third", "finally", "overall", "notably",
    "importantly", "indeed", "specifically", "interestingly", "ultimately", "collectively", "crucially",
    "as such", "in turn", "to this end", "in this regard", "in light of this", "with this in mind",
    "against this backdrop", "in doing so", "by doing so", "taken together", "in short", "put simply",
    "simply put", "in essence", "at its core", "more broadly", "more importantly", "conversely", "likewise",
    "similarly", "accordingly", "nevertheless", "nonetheless", "meanwhile", "subsequently", "to that end",
    "at a high level", "formally", "concretely", "intuitively", "in practice", "in principle", "looking ahead",
    "from a practical standpoint", "from a practical perspective", "from a cost perspective", "in this sense",
    "in other words", "put differently", "that said", "with that said", "all in all", "in summary",
]
# English openers (E4): the AI-typical ones are reported always; any other participial opener only when the main
# clause after the comma starts with a subject that cannot perform the participle (a dangling modifier)
AI_OPENER = (r"^(leveraging|harnessing|capitalizing on|building (up)?on|drawing (up)?on|grounded in|equipped with|"
             r"armed with|recognizing|acknowledging|having established|by (leveraging|integrating|combining|harnessing|"
             r"incorporating|employing|utilizing|bridging|unifying|marrying|coupling|synergizing))\b[^.;]{0,90},\s")
PARTICIPLE_OPENER = r"^(by \w+ing|\w{3,}ing|based on|compared (to|with)|using)\b[^,.;]{0,90},\s+"
NON_AGENT_SUBJECT = (r"(the (results?|findings?|performance|accuracy|errors?|data|outputs?|analysis|table|figure|"
                     r"evaluation|experiments?|numbers?|scores?|values?)|it|this|these|there|accuracy|performance)\b")
# English expletive and cleft constructions (E5)
EXPLETIVE = (r"^(there (is|are|exists?|was|were|remains?) (a |an |no |many |several |various |numerous |some )?|"
             r"it is (also |\w+ly )?(important|essential|crucial|critical|necessary|worth|clear|evident|possible|"
             r"noteworthy|interesting|notable|vital)\b|it is (\w+ )?(that|this|these|the) [^.]{1,60}\b(that|which|who)\b)")
CORRECTIVE = (r"\b(should|must|can) (be|instead be) (treated|understood|read|viewed|seen|interpreted|regarded) as\b"
              r"[^.]{0,80}\brather than\b|\bdoes not,? (by itself|on its own|in itself)\b|\bshould not be confused with\b|"
              r"\bis best (understood|seen|read|viewed) as\b|\bis less about\b[^.]{0,60}\bthan\b|"
              r"\bthe (question|point|goal) is not (whether|to|that)\b|\bnot because\b[^.]{0,60}\bbut because\b|"
              r"\b(is|are) not \w+( \w+)?; (it|they) \w+|\bnot without (its )?(limitations|merit|cost)\b|"
              r"\bthe (difficulty|challenge|problem|issue) (is not|does not lie)\b")
IRREGULAR_PARTICIPLES = (r"(shown|done|made|known|given|taken|found|seen|written|built|run|set|kept|held|chosen|drawn|"
                         r"left|put|read|sent|spent|thought|told|brought|bought|caught|taught|understood|undertaken|"
                         r"begun|driven|grown|hidden|laid|led|lost|meant|paid|said|sold|split|spread|struck|won|"
                         r"withdrawn|broken|frozen|stolen|proven|overridden|rewritten)")
# words that open a sentence as a transition only when a comma follows (otherwise they are ordinary subjects)
AMBIGUOUS_TRANSITIONS = {"kedua", "ketiga", "keempat", "hasilnya", "jelas", "terakhir", "first", "second", "third",
                         "lalu", "kemudian", "berikutnya", "maka", "jadi"}
FRONT_ADVERBIAL = (r"(jika|bila|apabila|ketika|saat|sewaktu|karena|sebab|meskipun|meski|walaupun|walau|dengan|tanpa|"
                   r"pada|untuk|dari|dalam|di antara|di|setelah|sesudah|sebelum|selama|berdasarkan|menurut|sebagai|"
                   r"sebagaimana|seperti|berbeda dengan|sama seperti|selain|sesuai|sejak|hingga|sampai|melalui|lewat|"
                   r"atas|terhadap|bagi|secara|demi|agar|supaya|semakin|makin|"
                   r"when|if|while|although|because|since|with|without|on|in|for|after|before|during|given)")
REVEAL = (r"^(inilah|itulah|di sinilah|di situlah|yang (\w+ ){0,2}(adalah|ialah|justru)\b|"
          r"yang (lebih |paling )?(menarik|penting|jelas|didukung|terlihat)\w* (hanya)\b|kuncinya|jawabannya|"
          r"hasilnya (jelas|sederhana)|here is|here's|this is where|that is (precisely|exactly)|the key is|"
          r"the answer is|what matters)")
NOMINAL = (r"\b(melakukan|memberikan|memberi|menghasilkan|mengalami|dilakukan(nya)?|dilakukan oleh|proses|"
           r"perform\w*|conduct\w*|carr\w* out)\s+(suatu |sebuah |an? |the )?(evaluasi|analisis|pengujian|uji|"
           r"perhitungan|pemeriksaan|perbandingan|penilaian|pengukuran|peningkatan|penurunan|perubahan|dampak|"
           r"kontribusi|pengaruh|validasi|verifikasi|pelatihan|implementasi|identifikasi|evaluation|analysis|"
           r"comparison|assessment|measurement|investigation)\b")
NOMINAL_FIRST = (r"\b(pengujian|analisis|evaluasi|perhitungan|pemeriksaan|perbandingan|penilaian|pengukuran|validasi|"
                 r"verifikasi|pelatihan|implementasi|pengumpulan data|identifikasi)\s+(\w+\s+){0,2}dilakukan\b")
POINTER = (r"(seperti|sebagaimana) (yang )?(telah |sudah )?(dijelaskan|disebutkan|dibahas|diuraikan)"
           r"( sebelumnya| di atas)?|(uraian|pemaparan|penjelasan) di atas|"
           r"as (mentioned|discussed|described) (earlier|above|previously)")
CLOSERS = ["secara keseluruhan", "dengan demikian", "singkatnya", "kesimpulannya", "hal ini menunjukkan",
           "dengan kata lain", "intinya", "overall", "in summary", "in conclusion", "taken together"]
SIGNPOST = (r"(bagian ini (akan )?(membahas|menjelaskan|menyajikan|memaparkan|menguraikan)|pada bagian ini|"
            r"bagian (berikut(nya)?|\w+) (membahas|menjelaskan|menyajikan|berisi|memaparkan)|"
            r"akan (dibahas|dijelaskan|dipaparkan|diuraikan)|berikut ini|sistematika penulisan|"
            r"disusun sebagai berikut|this section (presents|describes|discusses)|organized as follows|"
            r"section \w+ (discusses|presents|describes|reviews|details|reports))")
GLOSS = r"\b(yaitu|yakni|artinya|dengan kata lain|i\.e\.|that is,|in other words)"
HEDGES = (r"\b(dapat|mungkin|kemungkinan|berpotensi|cenderung|diduga|tampaknya|barangkali|relatif|agak|diperkirakan|"
          r"diharapkan|mengindikasikan|may|might|could|potentially|possibly|perhaps|likely|suggests?)\b")
FIRST_PERSON_ID = r"\b(kami|kita|saya|penulis)\b"
FIRST_PERSON_EN = r"\b(we|our|us)\b"
NOT_PASSIVE = {"diri", "dini", "dinas", "digital", "diskusi", "diskon", "dimensi", "distribusi", "dividen", "diagram",
               "dialog", "diploma", "direktur", "direksi", "disiplin", "disertasi", "diet", "dia", "dimana", "dinamis",
               "dinamika", "diagnostik", "diagnosis", "dictionary", "different", "difference", "direct", "directly",
               "discuss", "distinct", "distribution", "dimension", "dilema", "diversity", "divisi", "diskrit",
               "diferensial", "dikotomi", "dirinya", "dimulai"}
NOT_PASSIVE_TER = {"terhadap", "terutama", "terakhir", "tertentu", "termasuk", "terlalu", "terpisah", "tersebut",
                   "terbuka", "terbatas", "terbaik", "terbesar", "terkecil", "terdekat", "terendah", "tertinggi",
                   "terbaru", "terlama", "terlebih", "terjadi", "terdiri", "tersedia", "terkait", "ternyata",
                   "terdapat", "tergantung", "terlihat", "terasa"}
# words ending in -ly that are not manner or sentence adverbs
NOT_LY_ADVERB = {"only", "early", "family", "apply", "supply", "reply", "july", "italy", "rely", "ally", "holy", "ugly",
                 "likely", "unlikely", "monthly", "yearly", "daily", "weekly", "quarterly", "hourly", "assembly",
                 "anomaly", "fly", "imply", "comply", "multiply", "friendly", "costly", "timely", "elderly", "orderly",
                 "scholarly", "lonely", "lovely", "silly", "bully", "jelly", "belly", "rally", "tally", "italy",
                 "apply", "poly", "underly", "fully-connected", "lily", "emily", "butterfly", "firefly", "nightly"}
ID_ADVERB = (r"\bsecara \w+|\bdengan (baik|cepat|tepat|mudah|jelas|efektif|efisien|optimal|signifikan|sempurna|"
             r"maksimal|akurat|konsisten|lancar|benar|cermat|seksama)\b")
MONTHS = r"(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember|\d{4})"


# ---------------------------------------------------------------------------------------------------------------
# LaTeX to prose, keeping line numbers
# ---------------------------------------------------------------------------------------------------------------
SKIP_ENVS = (r"(table\*?|figure\*?|equation\*?|align\*?|gather\*?|multline\*?|algorithm\*?|algorithmic|tikzpicture|"
             r"tabular\*?|tabularx|verbatim|lstlisting|thebibliography|IEEEbiography|displaymath)")


def blank_keep_lines(m):
    return re.sub(r"[^\n]", " ", m.group(0))


def latex_to_prose(raw):
    """Plain prose with the same line numbers as the source: removed blocks keep their newlines."""
    t = re.sub(r"(?<!\\)%[^\n]*", "", raw)
    t = re.sub(r"\\begin\{" + SKIP_ENVS + r"\}.*?\\end\{\1\}", blank_keep_lines, t, flags=re.S)
    t = re.sub(r"\\\[.*?\\\]", blank_keep_lines, t, flags=re.S)
    t = re.sub(r"\$\$.*?\$\$", blank_keep_lines, t, flags=re.S)
    t = re.sub(r"\\(documentclass|usepackage|newcommand|renewcommand|DeclareRobustCommand|def|label|bibliography\w*|"
               r"input|include|includegraphics|newcolumntype|tikzset|usetikzlibrary|maketitle|author)\b[^\n]*", "", t)
    t = re.sub(r"~?\\(cite|citep|citet)\{[^}]*\}", " [c]", t)
    t = re.sub(r"\\(ref|eqref|autoref|cref|pageref)\{[^}]*\}", "1", t)
    t = re.sub(r"\$[^$]*\bp\s*(=|<|>|\\leq|\\geq|\\le|\\ge)[^$]*\$", "p=X", t)   # keep p-values visible to K8
    t = re.sub(r"\$\s*\\(rightarrow|to|Rightarrow|longrightarrow)\s*\$", " → ", t)
    t = re.sub(r"\$[^$]*\$", "X", t)
    t = re.sub(r"\\IEEEPARstart\{(\w)\}\{(\w*)\}", r"\1\2", t)
    for _ in range(3):
        t = re.sub(r"\\(en|emph|textit|textbf|texttt|textsc|textrm|mbox|url|href\{[^}]*\})\{([^{}]*)\}", r"\2", t)
    # headings, items and short environments are marked in place; no newline is added, so line numbers stay true
    t = re.sub(r"\\(section|subsection|subsubsection|paragraph|title|caption)\*?\{([^{}]*)\}", r"§HEAD \2", t)
    t = re.sub(r"\\item\b(\[[^\]]*\])?", "§ITEM ", t)
    t = re.sub(r"\\begin\{(abstract)\}", "§ABS ", t)
    t = re.sub(r"\\begin\{(IEEEkeywords|definisi|definition|theorem|lemma|proposition|corollary|proof|"
               r"keywords)\}(\[[^\]]*\])?", "§ENV ", t)
    t = re.sub(r"\\(begin|end)\{[^}]*\}(\[[^\]]*\])?", "", t)
    t = t.replace("~", " ").replace("\\%", "%").replace("``", '"').replace("''", '"').replace("\\ ", " ")
    t = re.sub(r"\\[a-zA-Z]+\*?", "", t)
    t = t.replace("{", "").replace("}", "").replace("\\", "")
    return t


def paragraphs_with_lines(text):
    """(first line, paragraph) pairs; a heading or item line always starts a new paragraph."""
    out, buf, start = [], [], None
    for i, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if buf and (not s or s.startswith(("§HEAD", "§ITEM"))):
            out.append((start, " ".join(buf)))
            buf, start = [], None
        if s:
            if start is None:
                start = i
            buf.append(s)
            if s.startswith("§HEAD"):
                out.append((start, " ".join(buf)))
                buf, start = [], None
    if buf:
        out.append((start, " ".join(buf)))
    return out


ABBREV = (r"\b(dkk|mis|dll|dsb|hlm|No|no|vs|et al|e\.g|i\.e|Figs?|Gbr|Tab|Eqs?|Pers|Secs?|Sect|Refs?|cf|resp|ca|viz|"
          r"approx|Dr|Prof|Jl|PT|Tbk|Rp|Inc|Ltd|Co|Corp|St|Mr|Ms|Mrs|Ch|pp|vol|Vol)\.")


def sentences(par):
    p = re.sub(ABBREV, lambda m: m.group(0).replace(".", "\u0001"), par)
    p = re.sub(r"(\d)\.(\d)", "\\1\u0001\\2", p)
    parts = re.split(r"(?<=[.!?])\s+(?=[\"(\[]?[A-Z0-9\\§])", p)
    return [s.replace("\u0001", ".").strip() for s in parts if len(s.split()) >= 2]


def words(s):
    return re.findall(r"[\w'-]+", s)


EN_PASSIVE = (r"\b(is|are|was|were|been|being|be)\s+(\w+ly\s+)?(\w+ed|" + IRREGULAR_PARTICIPLES + r")\b")


def is_passive(sentence):
    """Main-clause passive, roughly: a di-/ter- verb or be + participle that does not sit inside a relative clause
    ('yang ...', 'that/which/who ...')."""
    ws = words(sentence.lower())
    for i, w in enumerate(ws):
        relative = i > 0 and ws[i - 1] in ("yang", "telah", "sudah", "akan", "sedang") and \
            ("yang" in ws[max(0, i - 3):i])
        if relative:
            continue
        if re.fullmatch(r"di[a-z]{3,}", w) and w not in NOT_PASSIVE:
            return True
        if re.fullmatch(r"ter[a-z]{4,}(kan|i)?", w) and w not in NOT_PASSIVE_TER:
            return True
    s = re.sub(r"\b(that|which|who|whom)\b[^,.;]*", " ", sentence.lower())
    return bool(re.search(EN_PASSIVE, s))


def starts_with_transition(sl):
    """The transition a sentence opens with, or None. Ambiguous words count only when a comma follows."""
    for t in sorted(TRANSITIONS, key=len, reverse=True):
        if re.match(re.escape(t) + r"\s*,", sl):
            return t
        if t not in AMBIGUOUS_TRANSITIONS and re.match(re.escape(t) + r"\b", sl):
            return t
    return None


def scan_paragraph(par, english, synonyms):
    hits = []
    low = par.lower()
    sents = sentences(par)
    for rule, pats in VOCAB.items():
        if rule == "E2":
            continue
        for pat in pats:
            m = re.search(r"\b" + pat + r"\b", low)
            if m:
                hits.append((rule, f"kata '{m.group(0)}'"))
    if english:
        soft = sorted({m.group(0) for pat in VOCAB["E2"] for m in re.finditer(r"\b" + pat + r"\b", low)})
        if len(soft) >= 2:
            hits.append(("E2", f"{len(soft)} kosakata AI lunak dalam satu paragraf {soft}"))
        rather = len(re.findall(r"\brather than\b", low))
        if rather >= 2:
            hits.append(("E3", f"'rather than' {rather} kali dalam satu paragraf"))
    passive = [is_passive(s) for s in sents]
    if len(sents) >= 5 and sum(passive) / len(sents) > 0.6:
        hits.append(("K5", f"{sum(passive)} dari {len(sents)} kalimat pasif (di atas 60%)"))
    if len(re.findall(r"\bmerupakan\b", low)) >= 2:
        hits.append(("B2", f"'merupakan' {len(re.findall(r'merupakan', low))} kali"))
    for group in synonyms:
        used = [t for t in group if re.search(r"\b" + re.escape(t.lower()) + r"\b", low)]
        if len(used) >= 2:
            hits.append(("B5", f"istilah sinonim dalam satu paragraf: {used}"))
    trans_starts = []
    for s in sents:
        sl = s.lower().lstrip('"([')
        t = starts_with_transition(sl)
        if t:
            trans_starts.append(t)
        if t and re.match(re.escape(t) + r"\s*,", sl):
            hits.append(("K6", f"dibuka kata sambung berkoma: {s[:70]}"))
        elif not t and re.match(FRONT_ADVERBIAL + r"\b[^,.;]{2,70},\s", sl):
            hits.append(("K6", f"frasa keterangan di depan: {s[:70]}"))
        if re.match(r"\d", s):
            hits.append(("K11", f"kalimat dibuka angka: {s[:50]}"))
        n = len(words(s))
        if n > 35:
            hits.append(("K3", f"kalimat {n} kata: {s[:60]}"))
        if s.rstrip('")').endswith("?"):
            hits.append(("P15", f"pertanyaan retoris: {s[:60]}"))
        if re.search(r"\b(signifikan\w*|significant\w*)\b", s.lower()) and \
                not re.search(r"\bp\s*[=<>]|\bCI\b|selang kepercayaan|p-value|confidence interval", s):
            hits.append(("K8", f"'signifikan' tanpa p/CI: {s[:60]}"))
        hedge = re.search(HEDGES + r"(\s+\w+){0,2}?\s+" + HEDGES, s.lower())
        if hedge:
            hits.append(("K9", f"hedging bertumpuk '{hedge.group(0)}'"))
        if re.search(r"\b(berubah|bergeser|shifts?|moves?|changes?)\s+(sebesar|by)\s*[-−+]", s.lower()) or \
                re.search(r"\b(perbedaannya|selisihnya) (adalah|sebesar)\b|\bthe difference is\b", s.lower()):
            hits.append(("P7", f"kerangka laporan hasil: {s[:60]}"))
        if re.search(r"\b(menurunkan|turun|berkurang|lowers?|drops?|falls?|decreases?|reduces?)\b[^.]{0,60}"
                     r"(sebesar|by)?\s*[-−]\s?\d", s.lower()):
            hits.append(("P23", f"negatif ganda: {s[:60]}"))
        if re.search(r":\s+[a-z]", s) and not re.search(r":\s+[^.]*(,|;).*\b(dan|atau|and|or)\b", s) and \
                not re.search(r"\b(berikut|sebagai berikut|yaitu|antara lain|misalnya|contoh\w*)\s*:", s.lower()):
            hits.append(("P14", f"titik dua penyambung: {s[:60]}"))
        if re.search(r", (yang|which) [^,]{3,60}, ", s):
            hits.append(("P11", f"aposisi/sisipan di tengah kalimat: {s[:60]}"))
        if re.search(r",(?!\d)\s*(sehingga|so)\b[^.]*,(?!\d)\s*(sehingga|dan|yang|so|and|which)\b", s.lower()):
            hits.append(("P6", f"rantai klausa berkoma: {s[:60]}"))
        if re.search(r",\s*((yang|sehingga|dan)\s+)?(menunjukkan|memastikan|mencerminkan|menegaskan|menandakan|"
                     r"memungkinkan)\b|,\s*(highlighting|ensuring|reflecting|showcasing|underscoring|demonstrating|"
                     r"thereby \w+ing|making it|enabling|allowing|opening|paving|leaving|providing|offering|"
                     r"creating|yielding|confirming|representing|reinforcing)\b", s.lower()):
            hits.append(("P17", f"ekor kalimat dangkal: {s[:60]}"))
        if re.match(REVEAL, sl) or re.search(r"\b(inilah|itulah|sinilah|situlah|\w+nyalah)\b", sl):
            hits.append(("P26", f"kalimat pengungkap/penegas: {s[:60]}"))
        agent = re.search(r"\b(di[a-z]{3,}(kan|i)?\s+oleh|(\w+ed|" + IRREGULAR_PARTICIPLES + r")\s+by)\s+"
                          r"(the |a |an |para |sang )?(\w+)", sl)
        if agent and is_passive(s) and agent.group(6) not in ("default", "hand", "means", "far", "design", "construction"):
            hits.append(("K5", f"pasif dengan pelaku disebut (tulis aktif?): '{agent.group(0)}'"))
        if english:
            opener = re.match(PARTICIPLE_OPENER, sl)
            if re.match(AI_OPENER, sl):
                hits.append(("E4", f"pembuka partisip khas AI: {s[:60]}"))
            elif opener and not t and re.match(NON_AGENT_SUBJECT, sl[opener.end():]):
                hits.append(("E4", f"dangling modifier (subjek bukan pelaku partisip): {s[:60]}"))
            if re.match(EXPLETIVE, sl):
                hits.append(("E5", f"konstruksi ekspletif/cleft: {s[:60]}"))
            if re.search(r",\s*which (shows|means|indicates|suggests|highlights|demonstrates|underscores|confirms|"
                         r"makes|allows|enables|leads|results|ensures|reflects|is (important|crucial|critical|"
                         r"essential|key|significant))\b", sl):
                hits.append(("P17", f"ekor ', which ...' yang mengomentari kalimat: {s[:60]}"))
        if re.search(CORRECTIVE, sl):
            hits.append(("E3", f"framing korektif: {s[:60]}"))
        if len(re.findall(r"\byang\b", sl)) >= 4:
            hits.append(("K1", f"{len(re.findall(r'yang', sl))} 'yang' dalam satu kalimat: {s[:60]}"))
        if english:
            ly = [w for w in re.findall(r"\b[a-z]{3,}ly\b", sl) if w not in NOT_LY_ADVERB]
            if len(ly) >= 2:
                hits.append(("P20", f"{len(ly)} adverbia -ly dalam satu kalimat {ly}"))
        nominal = re.search(NOMINAL, s.lower()) or re.search(NOMINAL_FIRST, s.lower())
        if nominal:
            hits.append(("K4", f"tindakan di kata benda: '{nominal.group(0)}'"))
        if "!" in s:
            hits.append(("F6", f"tanda seru: {s[:60]}"))
        if re.search(r"→|->|=>|⇒", s):
            hits.append(("P22", f"panah di prosa: {s[:60]}"))
        if re.search(r"\b(beberapa|banyak)\b", s.lower()) and not re.search(r"\d", s) and not english:
            hits.append(("B6", f"kuantor kabur tanpa angka: {s[:60]}"))
        if re.search(r"\b(para ahli|banyak (penelitian|peneliti|studi|perusahaan)|sebagian besar (penelitian|studi)"
                     r"( sebelumnya)?|studi menunjukkan|(?<!hasil )penelitian (sebelumnya )?menunjukkan|"
                     r"experts? (believe|say)|studies (show|suggest)|research shows)\b", s.lower()) and "[c]" not in s:
            hits.append(("P18", f"atribusi kabur tanpa sitasi: {s[:60]}"))
        if re.search(r"\bsalah satu \w+( \w+)? (yang )?(ter[a-z]{4,}|paling)\b", s.lower()) and "[c]" not in s:
            hits.append(("W6", f"'salah satu ... ter-/paling' tanpa sitasi: {s[:60]}"))
    chains = [s for s in sents if len(re.findall(r",(?!\d)", s)) - s.count("(") >= 2 and len(words(s)) > 18]
    if len(chains) >= 2:
        hits.append(("P6", f"{len(chains)} kalimat berisi rangkaian klausa dengan koma"))
    if re.search(r"(tidak hanya|bukan hanya|bukan sekadar|not only|not just)\b.{0,120}\b(tetapi|melainkan|namun|but)\b", low) \
            or re.search(r"not (merely|just|simply)[^.]{0,80}[;,]\s*(it is|but)", low):
        hits.append(("P4", "pola 'tidak hanya X, tetapi juga Y'"))
    if re.search(r"\bdi satu sisi\b.*\bdi sisi (lain|yang lain)\b|\bon the one hand\b", low):
        hits.append(("P4", "keseimbangan semu 'di satu sisi ... di sisi lain'"))
    if len(re.findall(r"\bbukan\b[^.]{1,60},\s*(melainkan|tetapi)\b", low)) >= 1:
        hits.append(("P4", "kerangka kontras 'bukan X, melainkan Y'"))
    m = re.search(r"\bdari\s+(\w+)(\s\w+)?\s+(hingga|sampai)\s+(\w+)", low)
    if m and not re.match(r"[\d.,]+$|" + MONTHS, m.group(1)) and not re.match(MONTHS, m.group(4)):
        hits.append(("P5", "kemungkinan rentang palsu 'dari X hingga Y' (periksa skalanya)"))
    if re.search(r"—|–(?!\d)|\s---\s|\w---\w|[a-z]\s--\s[a-z]", par):
        hits.append(("P13", "em dash atau dash di antara kata"))
    enum = re.findall(r"\b(pertama|kedua|ketiga|keempat|first|second|third)\b\s*,", low)
    if len(enum) >= 2:
        hits.append(("P8", f"kerangka enumerasi {enum}"))
    glosses = re.findall(GLOSS, low)
    paren = [x for x in re.findall(r"\(([^()]*)\)", par)
             if len(x.split()) >= 3 and not re.search(r"\[c\]|\d|^(lihat|see|Tabel|Gambar|Table|Fig)", x)]
    if len(glosses) + len(paren) >= 2:
        hits.append(("P9", f"{len(glosses) + len(paren)} glos dalam satu paragraf {glosses + paren[:2]}"))
    this_starts = [s for s in sents if re.match(r"\"?(hal ini|hal tersebut|ini|this|these)\b", s.lower())]
    if len(this_starts) >= 2:
        hits.append(("P10", f"{len(this_starts)} kalimat diawali Hal ini/Ini/This/These"))
    if len(trans_starts) >= 2:
        hits.append(("P16", f"{len(trans_starts)} kalimat diawali kata transisi {trans_starts}"))
    if sents and any(sents[-1].lower().startswith(c) for c in CLOSERS):
        hits.append(("W2", f"penutup paragraf generik: {sents[-1][:60]}"))
    if re.search(SIGNPOST, low):
        hits.append(("W3", "penanda arah tanpa isi"))
    fp = set(re.findall(FIRST_PERSON_EN if english else FIRST_PERSON_ID, low))
    if english and re.search(r"(?<![A-Za-z.])I(?![A-Za-z.])", par.replace("Table I", "").replace("Section I", "")):
        fp.add("I")
    if fp:
        hits.append(("K5", f"kata ganti orang pertama {sorted(fp)}"))
    run = best = 0
    for s in sents:
        run = run + 1 if is_passive(s) else 0
        best = max(best, run)
    if best > 3:
        hits.append(("K5", f"{best} kalimat pasif berturut-turut"))
    toks = [s.split()[:2] for s in sents]
    for i in range(len(toks) - 2):
        a, b, c = toks[i], toks[i + 1], toks[i + 2]
        ids = all(len(x) > 1 and re.search(r"\d", x[1]) for x in (a, b, c))
        if a[0].lower() == b[0].lower() == c[0].lower() and not ids:
            hits.append(("P1", f"tiga kalimat berturut dibuka '{a[0]}'"))
            break
    lens = [len(words(s)) for s in sents]
    for i in range(len(lens) - 2):
        trio = lens[i:i + 3]
        if max(trio) <= 15 and max(trio) - min(trio) <= 3:
            hits.append(("P1", f"tiga kalimat pendek sejajar ({trio} kata)"))
            break
    triples = re.findall(r"\b\w+, \w+(?: \w+)?, (?:dan|serta|and) \w+\b", par)
    if len(triples) >= 2:
        hits.append(("P3", f"{len(triples)} daftar tiga butir dalam satu paragraf"))
    if re.search(r"\b(dll|dsb|dan lain-lain|dan sebagainya|dan seterusnya|etc)\b", low):
        hits.append(("W6", "'dan lain-lain' atau sejenisnya di naskah ilmiah"))
    if not english and re.search(r"(?<![\d.])(?<!bagian )(?<!tabel )(?<!gambar )(?<!versi )(?<!python )\d+\.\d{1,2}(?![\d.])", low):
        hits.append(("K11", "titik desimal di naskah berbahasa Indonesia (pakai koma desimal)"))
    if re.search(r"\b(proporsi|rasio|fraksi|laju)\b[^.]{0,40}\b0,\d+\b", low) and re.search(r"\d+(,\d+)?\s?%", par):
        hits.append(("K11", "proporsi dan persen dicampur dalam satu paragraf"))
    if re.search(POINTER, low):
        hits.append(("W12", "penunjuk 'seperti dijelaskan sebelumnya'"))
    if english:
        ly = [w for w in re.findall(r"\b[a-z]{3,}ly\b", low) if w not in NOT_LY_ADVERB]
        if len(ly) >= 3:
            hits.append(("P20", f"{len(ly)} adverbia -ly dalam satu paragraf {ly[:6]}"))
    else:
        adv = [m.group(0) for m in re.finditer(ID_ADVERB, low)]
        if len(adv) >= 3:
            hits.append(("P20", f"{len(adv)} keterangan cara dalam satu paragraf {adv[:6]}"))
        if len(re.findall(r"\bserta\b", low)) >= 3:
            hits.append(("P25", f"'serta' {len(re.findall(r'serta', low))} kali dalam satu paragraf"))
    if not english:
        for w, lim, rule in (("sebuah", 3, "P25"), ("suatu", 3, "P25"), ("tersebut", 3, "P25"), ("telah", 3, "K10"),
                             ("sudah", 4, "K10")):
            n = len(re.findall(r"\b" + w + r"\b", low))
            if n >= lim:
                hits.append((rule, f"'{w}' {n} kali dalam satu paragraf"))
    n_words, n_sents = len(words(par)), len(sents)
    if n_sents and (n_sents < 3 or n_words < 50):
        hits.append(("W11", f"paragraf pendek ({n_sents} kalimat, {n_words} kata)"))
    if n_sents > 10 or n_words > 230:
        hits.append(("W11", f"paragraf panjang ({n_sents} kalimat, {n_words} kata)"))
    return hits, lens


def file_level(raw, prose, english=False):
    hits = []
    for c, name in (("\u201c", "kutip melengkung"), ("\u201d", "kutip melengkung"), ("\u2018", "kutip melengkung"),
                    ("\u2019", "kutip melengkung"), ("\u2026", "elipsis Unicode"), ("\u2014", "em dash Unicode")):
        if c in raw:
            hits.append(("F5", f"karakter {name} '{c}'"))
    for i, line in enumerate(raw.splitlines(), 1):
        s = line.strip()
        if s.startswith("%"):
            continue
        if re.search(r"\\textbf\{[^}]{2,40}([.:]\}|\}\s*[.:])", s) and "&" not in s and not s.startswith("\\item"):
            hits.append(("F2", f"baris {i}: label tebal di paragraf: {s[:70]}"))
        if re.search(r"\*\*|^#{1,4}\s|`[^`]+`", s) and not s.startswith("\\"):
            hits.append(("F5", f"baris {i}: sisa markdown: {s[:60]}"))
        if re.search(r"\$p\$\s*(\$<\$)?\s*\d|\bp\s+\d[.,]\d", s):
            hits.append(("F12", f"baris {i}: notasi p tanpa '=' atau '<': {s[:60]}"))
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", raw, re.S)
    if abstract:
        n = len(words(latex_to_prose(abstract.group(1))))
        if not 150 <= n <= 250:
            hits.append(("ABS", f"abstrak {n} kata (batas bawaan 150 sampai 250)"))
    body = re.sub(r"§ABS[^\n]*(\n[^\n]+)*", " ", prose)          # the abstract may repeat body sentences
    seen, undefined = set(), []
    skip = {"X", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "HEAD", "ITEM", "ENV", "ABS"}
    for m in re.finditer(r"\b([A-Z][A-Z0-9]{1,6}s?)\b", body):
        a = m.group(1)
        if a in seen or a in skip or re.fullmatch(r"[A-Z]\d+", a):
            continue
        seen.add(a)
        around = body[max(0, m.start() - 3):m.end() + 3]
        if "(" not in around and ")" not in around:
            undefined.append(a)
    if undefined:
        hits.append(("K11", f"singkatan yang kemunculan pertamanya tanpa definisi dalam kurung (periksa): "
                            f"{', '.join(undefined[:25])}"))
    toks = re.findall(r"[a-z0-9]+", re.sub(r"§\w+", " ", body.lower()))
    grams = Counter(" ".join(toks[i:i + 8]) for i in range(len(toks) - 7))
    kept = []
    for g in sorted(g for g, n in grams.items() if n >= 2 and not re.fullmatch(r"[\d x]+", g)):
        if not any(g[:25] in k or k[-25:] in g for k in kept):
            kept.append(g)
    if kept:
        hits.append(("W12", f"{len(kept)} rangkaian 8 kata muncul lebih dari sekali (gagasan berulang lintas "
                            f"bagian?): " + " | ".join(kept[:6])))
    for m in re.finditer(r"§HEAD ([^\n]+)", body):
        ws = [w for w in m.group(1).split() if len(w) > 3]
        if len(ws) >= 3 and all(w[0].isupper() for w in ws):
            hits.append(("F4", f"judul huruf kapital tiap kata: {m.group(1)[:60]}"))
    openers = Counter()
    for _, par in paragraphs_with_lines(body):
        if not par.startswith(("§HEAD", "§ITEM", "§ENV")) and len(words(par)) >= 30:
            openers[" ".join(words(par.lower())[:2])] += 1
    n_par = sum(openers.values())
    for op, n in openers.most_common(3):
        if n >= 4 and n >= 0.15 * n_par:
            hits.append(("W1", f"{n} dari {n_par} paragraf dibuka '{op} ...' (pembuka paragraf bertemplat)"))
    for i, block in enumerate(re.split(r"\n\s*\n", re.sub(r"(?<!\\)%[^\n]*", "", raw))):
        n_emph = len(re.findall(r"\\(emph|textit)\{", block))
        if n_emph >= 2 and not block.lstrip().startswith(("\\begin{table", "\\begin{figure")):
            line = raw.find(block.strip()[:40])
            hits.append(("F3", f"baris {raw[:line].count(chr(10)) + 1}: {n_emph} penekanan \\emph/\\textit dalam satu "
                               f"paragraf (istilah asing pakai makro istilah, bukan penekanan)"))
    if english:
        lw = body.lower()
        natural_ise = {"otherwise", "likewise", "precise", "exercise", "expertise", "advise", "devise", "revise",
                       "comprise", "concise", "premise", "enterprise", "compromise", "surprise", "raise", "promise",
                       "noise", "wise", "rise", "arise", "paradise", "franchise", "merchandise", "praise", "poise",
                       "clockwise", "pairwise", "stepwise", "elementwise", "pointwise", "noisewise", "chemise",
                       "disguise", "supervise", "televise", "improvise", "incise", "excise", "circumcise", "despise"}
        us = {w for w in re.findall(r"\b\w+(?:ize|izes|ized|izing|ization|izations|yze|yzed|yzing)\b", lw)}
        uk = {w for w in re.findall(r"\b\w+(?:ise|ises|ised|ising|isation|isations|yse|ysed|ysing)\b", lw)
              if not any(w.startswith(n) for n in natural_ise) and len(w) > 6}
        for a, b in (("color", "colour"), ("behavior", "behaviour"), ("modeling", "modelling"), ("center", "centre"),
                     ("labeled", "labelled"), ("favor", "favour"), ("program ", "programme")):
            if a in lw:
                us.add(a.strip())
            if b in lw:
                uk.add(b.strip())
        if us and uk:
            hits.append(("E8", f"ejaan Amerika dan Inggris tercampur: {', '.join(sorted(us)[:4])} / "
                               f"{', '.join(sorted(uk)[:4])}"))
        rather = len(re.findall(r"\brather than\b", lw))
        if 1000 * rather / max(1, len(words(body))) > 2:
            hits.append(("E3", f"'rather than' {rather} kali ({1000 * rather / max(1, len(words(body))):.1f} per "
                               f"1.000 kata; naskah manusia pembanding sekitar 0,5)"))
        ly_all = [w for w in re.findall(r"\b[a-z]{3,}ly\b", body.lower()) if w not in NOT_LY_ADVERB]
        rate = 1000 * len(ly_all) / max(1, len(words(body)))
        if rate > 12:
            hits.append(("P20", f"adverbia -ly {rate:.1f} per 1.000 kata (di atas 12; tersering: "
                                f"{', '.join(w for w, _ in Counter(ly_all).most_common(5))})"))
    fp_total = len(re.findall(r"\b(tidak hanya|bukan sekadar|bukan hanya|not only)\b", body.lower()))
    if fp_total > 1:
        hits.append(("P4", f"'tidak hanya/bukan sekadar' muncul {fp_total} kali di seluruh naskah (paling banyak sekali)"))
    novelty = len(re.findall(r"sejauh (pengetahuan|penelusuran)|to the best of (our|the authors') knowledge", body.lower()))
    if novelty > 1:
        hits.append(("F11", f"klaim 'sejauh pengetahuan' muncul {novelty} kali"))
    return hits


# rules that mark AI-typical wording; the others are style rules that careful human writers also break
AI_MARKERS = {"B1", "B2", "B3", "B7", "E1", "E2", "E3", "E4", "E6", "F6", "F13", "K9", "P4", "P7", "P10", "P16",
              "P17", "P19", "P20", "P26", "P27", "W2", "W3", "W14", "W15"}


def analyze(path, lang="auto", synonyms=(), only=()):
    """Findings of one file: dict with language, per-paragraph report lines, file-level hits, all (rule, msg)
    findings, sentence and paragraph lengths and word count."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    is_tex = path.endswith(".tex") or "\begin{document}" in raw
    prose = latex_to_prose(raw) if is_tex else raw
    if is_tex and "\begin{document}" in raw:
        offset = raw[:raw.index("\begin{document}")].count("\n")
        prose = "\n" * offset + latex_to_prose(raw[raw.index("\begin{document}"):])
    if lang == "auto":
        lw = prose.lower()
        english = len(re.findall(r"\b(the|and|of|is)\b", lw)) > len(re.findall(r"\b(yang|dan|dengan|ini)\b", lw))
    else:
        english = lang == "en"
    res = {"english": english, "out": [], "findings": [], "lengths": [], "plens": [], "words": 0}
    for line, par in paragraphs_with_lines(prose):
        if par.startswith("§HEAD") or len(words(par)) < 8:
            continue
        exempt = par.startswith(("§ENV", "§ITEM", "§ABS"))
        par = re.sub(r"§(ENV|ITEM|ABS)", "", par).strip()
        hits, lens = scan_paragraph(par, english, synonyms)
        if exempt:
            hits = [h for h in hits if h[0] not in ("W11", "P15")]
        res["lengths"] += lens
        res["plens"].append(len(words(par)))
        res["words"] += len(words(par))
        hits = [h for h in hits if not only or h[0] in only]
        res["findings"] += hits
        if hits:
            res["out"].append(f"baris {line}: {par[:70]}...")
            res["out"] += [f"    {r:<4} {msg}" for r, msg in hits]
    res["fhits"] = [h for h in file_level(raw, prose, english) if not only or h[0] in only]
    res["findings"] += res["fhits"]
    return res


def counts_line(findings):
    c = Counter(r for r, _ in findings)
    return ", ".join(f"{r} {n}" for r, n in sorted(c.items())) or "tidak ada"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--summary", action="store_true", help="only counts per rule")
    ap.add_argument("--rules", default="", help="comma-separated rule ids to show, e.g. K6,P6")
    ap.add_argument("--synonyms", default="", help='e.g. "knowledge base|KB|basis pengetahuan;LLM|model bahasa"')
    ap.add_argument("--lang", choices=["auto", "id", "en"], default="auto")
    ap.add_argument("--baseline", default="", help="the version before revision: report what is left, fixed, new")
    a = ap.parse_args()
    synonyms = [[t.strip() for t in g.split("|") if t.strip()] for g in a.synonyms.split(";") if g.strip()]
    only = {r.strip() for r in a.rules.split(",") if r.strip()}
    res = analyze(a.file, a.lang, synonyms, only)
    if a.baseline:
        base = analyze(a.baseline, a.lang, synonyms, only)
        left = Counter(res["findings"]) & Counter(base["findings"])
        new = Counter(res["findings"]) - Counter(base["findings"])
        fixed = Counter(base["findings"]) - Counter(res["findings"])
        print(f"sebelum: {counts_line(base['findings'])}")
        print(f"sesudah: {counts_line(res['findings'])}")
        print(f"\nhilang (diperbaiki atau kalimatnya berubah): {sum(fixed.values())}")
        print(f"TERTINGGAL (temuan yang sama masih ada): {sum(left.values())}")
        for (r, msg), n in sorted(left.items()):
            print(f"    {r:<4} {msg}" + (f"  (x{n})" if n > 1 else ""))
        print(f"BARU MUNCUL (kemungkinan dibuat oleh perbaikan): {sum(new.values())}")
        for (r, msg), n in sorted(new.items()):
            print(f"    {r:<4} {msg}" + (f"  (x{n})" if n > 1 else ""))
        print("\nUlangi revisi dan pemindaian sampai TERTINGGAL dan BARU MUNCUL hanya berisi temuan yang sengaja "
              "dipertahankan beserta alasannya.")
        return 0
    if not a.summary:
        print("\n".join(res["out"]))
        if res["fhits"]:
            print("tingkat berkas:")
            print("\n".join(f"    {r:<4} {msg}" for r, msg in res["fhits"]))
        print()
    print(f"bahasa: {'Inggris' if res['english'] else 'Indonesia'}")
    print("temuan per aturan: " + counts_line(res["findings"]))
    n_ai = sum(1 for r, _ in res["findings"] if r in AI_MARKERS)
    print(f"penanda AI: {n_ai} temuan, {1000 * n_ai / max(1, res['words']):.1f} per 1.000 kata "
          f"(aturan gaya lain: {len(res['findings']) - n_ai})")
    lengths, plens = res["lengths"], res["plens"]
    if lengths:
        print(f"panjang kalimat: n={len(lengths)}, median {statistics.median(lengths):.0f}, min {min(lengths)}, "
              f"maks {max(lengths)}, SD {statistics.pstdev(lengths):.1f} (SD di bawah 6 berarti ritme seragam)")
    if plens:
        print(f"panjang paragraf (kata): n={len(plens)}, median {statistics.median(plens):.0f}, min {min(plens)}, "
              f"maks {max(plens)}")


if __name__ == "__main__":
    sys.exit(main())
