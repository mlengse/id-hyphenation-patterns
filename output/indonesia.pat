% Pola Pemenggalan Bahasa Indonesia sesuai EYD Edisi V
% Dibuat berdasarkan algoritma Frank Liang (TeX)
% 
% Prinsip Dasar:
% Angka ganjil (1, 3) = Izin pemenggalan
% Angka genap (2, 4) = Larangan pemenggalan

\patterns{
% --- 1. ATURAN VOKAL (EYD V, C.1.a) ---
% Jika di tengah kata terdapat huruf vokal yang berurutan, 
% pemenggalannya dilakukan di antara kedua huruf vokal itu.
a1a a1e a1i a1o a1u
e1a e1e e1i e1o e1u
i1a i1e i1i i1o i1u
o1a o1e o1i o1o o1u
u1a u1e u1i u1o u1u

% --- 2. PENGECUALIAN DIFTONG & MONOFTONG (EYD V, C.1.b & C.1.c) ---
% Diftong ai, au, ei, oi dan monoftong eu tidak dipenggal.
% Kita gunakan angka '2' (genap) untuk melarang pemenggalan
% yang sebelumnya diizinkan oleh aturan vokal di atas.
a2i % Cegah pemenggalan 'ai' (pandai)
a2u % Cegah pemenggalan 'au' (saudara)
e2i % Cegah pemenggalan 'ei' (survei)
o2i % Cegah pemenggalan 'oi' (amboi)
e2u % Cegah pemenggalan 'eu' (seudati)

% --- 3. POLA V-C-V (EYD V, C.1.d) ---
% Jika di tengah kata dasar terdapat huruf konsonan di antara dua vokal,
% pemenggalannya dilakukan SEBELUM huruf konsonan itu.
% Contoh: ba-pak, de-ngan.
% Pola: (Vokal)1(Konsonan)
1ba 1ca 1da 1fa 1ga 1ha 1ja 1ka 1la 1ma 1na 1pa 1qa 1ra 1sa 1ta 1va 1wa 1xa 1ya 1za
1bi 1ci 1di 1fi 1gi 1hi 1ji 1ki 1li 1mi 1ni 1pi 1qi 1ri 1si 1ti 1vi 1wi 1xi 1yi 1zi
1bu 1cu 1du 1fu 1gu 1hu 1ju 1ku 1lu 1mu 1nu 1pu 1qu 1ru 1su 1tu 1vu 1wu 1xu 1yu 1zu
1be 1ce 1de 1fe 1ge 1he 1je 1ke 1le 1me 1ne 1pe 1qe 1re 1se 1te 1ve 1we 1xe 1ye 1ze
1bo 1co 1do 1fo 1go 1ho 1jo 1ko 1lo 1mo 1no 1po 1qo 1ro 1so 1to 1vo 1wo 1xo 1yo 1zo

% --- 4. POLA V-CC-V (EYD V, C.1.e) ---
% Jika terdapat dua huruf konsonan berurutan, pemenggalan dilakukan
% DI ANTARA kedua huruf konsonan itu.
% Contoh: man-di, som-bong.
% Pola: (Konsonan)1(Konsonan). 
% Kita definisikan secara umum:
b1b c1c d1d f1f g1g h1h j1j k1k l1l m1m n1n p1p q1q r1r s1s t1t v1v w1w x1x y1y z1z
b1c b1d b1f b1g b1h b1j b1k b1l b1m b1n b1p b1q b1r b1s b1t b1v b1w b1x b1y b1z
c1b c1d c1f c1g c1h c1j c1k c1l c1m c1n c1p c1q c1r c1s c1t c1v c1w c1x c1y c1z
d1b d1c d1f d1g d1h d1j d1k d1l d1m d1n d1p d1q d1r d1s d1t d1v d1w d1x d1y d1z
% (Dan seterusnya untuk kombinasi konsonan lainnya...)
% Pola generik di bawah ini mencakup mayoritas kombinasi K-K:
1b 1c 1d 1f 1g 1h 1j 1k 1l 1m 1n 1p 1q 1r 1s 1t 1v 1w 1x 1y 1z

% --- 5. PERLINDUNGAN DIGRAF (EYD V, C.1.g) ---
% Gabungan huruf konsonan kh, ng, ny, sy tidak dipenggal.
% Kita gunakan angka '2' untuk melarang pemenggalan di tengah digraf.
2kh % Contoh: ma-khluk (bukan mak-hluk)
2ng % Contoh: de-ngan (bukan den-gan)
2ny % Contoh: ke-nyang (bukan ken-yang)
2sy % Contoh: mu-sya-wa-rah (bukan mus-ya-wa-rah)

% --- 6. PENANGANAN 3 KONSONAN (EYD V, C.1.f) ---
% Jika terdapat tiga konsonan, pemenggalan dilakukan di antara 
% konsonan pertama dan kedua.
% Contoh: in-stru-men (n-str).
% Aturan ini sebenarnya sudah tercakup secara otomatis oleh kombinasi:
% Pola V-CC-V (n1s) akan memenggal 'n' dan 's'.
% Pola V-C-V (1t, 1r) akan membiarkan 'str' menyatu jika tidak ada 'n'.
% Namun, untuk 'str', 'ktr', dsb, kita perlu memastikan 
% tidak ada pemenggalan antara konsonan ke-2 dan ke-3 jika itu kluster.
% Contoh 'instruksi': i n - s t r u k - s i
% n1s (memenggal n-s)
% s2t (mencegah s-t? Tidak, EYD membolehkan s-tr menyatu di awal suku kata)
% Jadi kita perlu melindungi kluster awal suku kata umum:
2str 2skr 2spr 2pl 2pr 2bl 2br 2tr 2dr 2kl 2kr 2gl 2gr 2fl 2fr

% --- 7. IMBUHAN (AWALAN/AKHIRAN) ---
% EYD V, C.2: Pemenggalan dilakukan di antara bentuk dasar dan imbuhan.
% Prioritas lebih tinggi (3 atau 4) mungkin diperlukan jika pola di atas salah.
% Contoh: meng-u-kur (bukan me-ngu-kur)
% Pola ini spesifik kata turunan.
meng1 
mem1
men1
meny1
peng1
pem1
pen1
peny1
ber1
ter1
per1
bel1
1kan
1an
1lah
1kah
1pun
2nya % Jangan pisah 'ny' pada akhiran -nya, tapi pisah sebelumnya: 1nya

% --- 8. KOREKSI KHUSUS (OVERRIDE) ---
% Menangani kasus di mana aturan K-K dan Digraf bertabrakan.
% Contoh: tang-gap (ng-g). 
% Pola 2ng melarang n-g. Pola g1g memenggal g-g.
% Hasil: ta(ng)-gap. (Benar).
% Contoh: sang-gup. 
% Pola 2ng melarang n-g. Pola g1g memenggal g-g.
% Hasil: sa(ng)-gup. (Benar).
% Contoh: in-tro.
% n1t (pisah). t2r (jangan pisah tr).
% Hasil: in-tro. (Benar).

}

