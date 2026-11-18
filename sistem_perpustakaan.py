"""
Sistem Perpustakaan (versi GUI interaktif dengan Tkinter)
Universitas Bina Bangsa

Cara menjalankan:  python perpustakaan_gui.py
(Tkinter sudah termasuk di instalasi Python standar, tidak perlu install apa-apa.)

Materi OOP yang dipakai:
1. Class & Object              6. Inheritance & super()
2. Constructor (__init__)      7. Polymorphism (method overriding)
3. Class & instance attribute  8. Abstraction (abstract class)
4. Encapsulation (private)     9. Magic method (__str__)
5. Instance/class/static method 10. Composition (Perpustakaan punya Buku & Anggota)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod


# ===============================================================
#  BAGIAN 1 : CLASS OOP (logika program)
# ===============================================================
class Buku:
    def __init__(self, kode, judul, penulis, stok):
        self.kode = kode
        self.judul = judul
        self.penulis = penulis
        self.__stok = 0          # atribut private
        self.stok = stok         # lewat setter agar divalidasi

    @property
    def stok(self):
        return self.__stok

    @stok.setter
    def stok(self, nilai):
        if not isinstance(nilai, int):
            raise ValueError("Stok harus berupa bilangan bulat")
        if nilai < 0:
            raise ValueError("Stok tidak boleh negatif")
        self.__stok = nilai

    @property
    def tersedia(self):
        return self.__stok > 0

    def __str__(self):
        return f"[{self.kode}] {self.judul} - {self.penulis} (stok: {self.stok})"


class Anggota(ABC):
    jumlah_anggota = 0           # class attribute (anggota yang terdaftar)

    def __init__(self, nama, id_anggota):
        self.nama = nama
        self._id_anggota = id_anggota    # protected
        self.__pinjaman = []             # private

    @property
    def id_anggota(self):
        return self._id_anggota

    @property
    def daftar_pinjaman(self):
        return list(self.__pinjaman)

    def tambah_pinjaman(self, buku):
        if buku in self.__pinjaman:
            raise ValueError(f"{self.nama} sudah meminjam '{buku.judul}'")
        if len(self.__pinjaman) >= self.batas_pinjam():
            raise ValueError(
                f"{self.nama} sudah mencapai batas pinjam "
                f"({self.batas_pinjam()} buku)"
            )
        self.__pinjaman.append(buku)

    def hapus_pinjaman(self, buku):
        if buku not in self.__pinjaman:
            raise ValueError(f"{self.nama} tidak meminjam buku tersebut")
        self.__pinjaman.remove(buku)

    # Abstract method: wajib di-override oleh subclass
    @abstractmethod
    def batas_pinjam(self):
        pass

    @abstractmethod
    def peran(self):
        pass

    @abstractmethod
    def keterangan(self):
        pass

    @classmethod
    def total_anggota(cls):
        return cls.jumlah_anggota

    @classmethod
    def catat_anggota(cls):
        cls.jumlah_anggota += 1

    @staticmethod
    def validasi_id(id_anggota):
        return (isinstance(id_anggota, str)
                and len(id_anggota) >= 3
                and id_anggota.isalnum())

    def __str__(self):
        return f"[{self.peran()}] {self.nama} ({self.id_anggota})"


class Mahasiswa(Anggota):
    def __init__(self, nama, id_anggota, jurusan):
        super().__init__(nama, id_anggota)
        self.jurusan = jurusan

    def batas_pinjam(self):
        return 3

    def peran(self):
        return "Mahasiswa"

    def keterangan(self):
        return self.jurusan


class Dosen(Anggota):
    def __init__(self, nama, id_anggota, mata_kuliah):
        super().__init__(nama, id_anggota)
        self.mata_kuliah = mata_kuliah

    def batas_pinjam(self):
        return 5

    def peran(self):
        return "Dosen"

    def keterangan(self):
        return self.mata_kuliah


class Perpustakaan:
    def __init__(self, nama):
        self.nama = nama
        self.__buku = {}        # kunci: kode buku
        self.__anggota = {}     # kunci: id anggota

    # ---- data buku ----
    def tambah_buku(self, buku):
        if buku.kode in self.__buku:
            raise ValueError(f"Kode buku '{buku.kode}' sudah dipakai")
        self.__buku[buku.kode] = buku

    def daftar_buku(self):
        return list(self.__buku.values())

    def cari_buku(self, kode):
        buku = self.__buku.get(kode)
        if buku is None:
            raise ValueError("Buku tidak ditemukan")
        return buku

    # ---- data anggota ----
    def daftarkan_anggota(self, anggota):
        if not Anggota.validasi_id(anggota.id_anggota):
            raise ValueError(
                f"ID '{anggota.id_anggota}' tidak valid "
                "(minimal 3 karakter, hanya huruf/angka tanpa spasi)"
            )
        if anggota.id_anggota in self.__anggota:
            raise ValueError(f"ID '{anggota.id_anggota}' sudah terdaftar")
        self.__anggota[anggota.id_anggota] = anggota
        Anggota.catat_anggota()

    def daftar_anggota(self):
        return list(self.__anggota.values())

    def cari_anggota(self, id_anggota):
        anggota = self.__anggota.get(id_anggota)
        if anggota is None:
            raise ValueError("Anggota tidak ditemukan")
        return anggota

    # ---- transaksi ----
    def pinjam_buku(self, id_anggota, kode):
        anggota = self.cari_anggota(id_anggota)
        buku = self.cari_buku(kode)
        if not buku.tersedia:
            raise ValueError(f"Stok buku '{buku.judul}' habis")
        anggota.tambah_pinjaman(buku)
        buku.stok -= 1
        return f"{anggota.nama} berhasil meminjam '{buku.judul}'"

    def kembalikan_buku(self, id_anggota, kode):
        anggota = self.cari_anggota(id_anggota)
        buku = self.cari_buku(kode)
        anggota.hapus_pinjaman(buku)
        buku.stok += 1
        return f"{anggota.nama} mengembalikan '{buku.judul}'"


def isi_data_awal(perpus):
    """Data contoh supaya aplikasi tidak kosong saat pertama dibuka."""
    perpus.tambah_buku(Buku("B001", "Pemrograman Python", "Budi Raharjo", 2))
    perpus.tambah_buku(Buku("B002", "Algoritma dan Struktur Data", "Rinaldi Munir", 1))
    perpus.tambah_buku(Buku("B003", "Basis Data", "Abdul Kadir", 3))
    perpus.tambah_buku(Buku("B004", "Jaringan Komputer", "Andrew Tanenbaum", 2))
    perpus.daftarkan_anggota(
        Mahasiswa("Putri Eka Anindita", "MHS14012500121", "Ilmu Komputer"))
    perpus.daftarkan_anggota(
        Dosen("Andika Purnama, S.Kom., M.Kom.", "DSN231401227",
              "Pemrograman Berorientasi Objek 1"))


# ===============================================================
#  BAGIAN 2 : TAMPILAN (GUI Tkinter)
# ===============================================================
class AplikasiPerpustakaan(tk.Tk):
    def __init__(self, perpus):
        super().__init__()
        self.perpus = perpus
        self.title(perpus.nama)
        self.geometry("900x560")
        self.minsize(820, 500)

        # judul
        ttk.Label(self, text=f"📚 {perpus.nama}",
                  font=("Segoe UI", 15, "bold")).pack(pady=(10, 4))

        # tab
        self.tab = ttk.Notebook(self)
        self.tab.pack(fill="both", expand=True, padx=10, pady=6)
        self._buat_tab_buku()
        self._buat_tab_anggota()
        self._buat_tab_pinjam()

        # status bar
        self.status = tk.StringVar(value="Siap.")
        ttk.Label(self, textvariable=self.status, relief="sunken",
                  anchor="w", padding=4).pack(fill="x", side="bottom")

        self.refresh_semua()

    # ------------------------------------------------------------
    # TAB 1 : DAFTAR BUKU
    # ------------------------------------------------------------
    def _buat_tab_buku(self):
        frame = ttk.Frame(self.tab, padding=10)
        self.tab.add(frame, text="  Daftar Buku  ")

        kolom = ("kode", "judul", "penulis", "stok", "status")
        self.tree_buku = ttk.Treeview(frame, columns=kolom, show="headings", height=10)
        for k, teks, lebar in [("kode", "Kode", 70), ("judul", "Judul Buku", 280),
                               ("penulis", "Penulis", 180), ("stok", "Stok", 60),
                               ("status", "Status", 100)]:
            self.tree_buku.heading(k, text=teks)
            self.tree_buku.column(k, width=lebar,
                                  anchor="center" if k in ("kode", "stok", "status") else "w")
        self.tree_buku.tag_configure("habis", foreground="red")
        self.tree_buku.pack(fill="both", expand=True)

        form = ttk.LabelFrame(frame, text="Tambah Buku Baru", padding=10)
        form.pack(fill="x", pady=(10, 0))
        self.var_kode = tk.StringVar()
        self.var_judul = tk.StringVar()
        self.var_penulis = tk.StringVar()
        self.var_stok = tk.StringVar(value="1")
        isi = [("Kode Buku", self.var_kode, 10), ("Judul", self.var_judul, 28),
               ("Penulis", self.var_penulis, 20), ("Stok", self.var_stok, 6)]
        for i, (label, var, lebar) in enumerate(isi):
            ttk.Label(form, text=label).grid(row=0, column=i, sticky="w", padx=4)
            ttk.Entry(form, textvariable=var, width=lebar).grid(row=1, column=i, padx=4)
        ttk.Button(form, text="Tambah Buku",
                   command=self.aksi_tambah_buku).grid(row=1, column=4, padx=10)

    def aksi_tambah_buku(self):
        kode = self.var_kode.get().strip().upper()
        judul = self.var_judul.get().strip()
        penulis = self.var_penulis.get().strip()
        try:
            if not (kode and judul and penulis):
                raise ValueError("Kode, judul, dan penulis wajib diisi")
            try:
                stok = int(self.var_stok.get())
            except ValueError:
                raise ValueError("Stok harus berupa angka")
            self.perpus.tambah_buku(Buku(kode, judul, penulis, stok))
        except ValueError as e:
            self._error(e)
            return
        for v in (self.var_kode, self.var_judul, self.var_penulis):
            v.set("")
        self.var_stok.set("1")
        self._sukses(f"Buku '{judul}' ({kode}) berhasil ditambahkan")

    # ------------------------------------------------------------
    # TAB 2 : ANGGOTA
    # ------------------------------------------------------------
    def _buat_tab_anggota(self):
        frame = ttk.Frame(self.tab, padding=10)
        self.tab.add(frame, text="  Anggota  ")

        kolom = ("id", "nama", "peran", "keterangan", "batas", "dipinjam")
        self.tree_anggota = ttk.Treeview(frame, columns=kolom, show="headings", height=10)
        for k, teks, lebar in [("id", "ID Anggota", 130), ("nama", "Nama", 220),
                               ("peran", "Peran", 90), ("keterangan", "Jurusan / Mata Kuliah", 220),
                               ("batas", "Batas", 55), ("dipinjam", "Dipinjam", 70)]:
            self.tree_anggota.heading(k, text=teks)
            self.tree_anggota.column(k, width=lebar,
                                     anchor="center" if k in ("batas", "dipinjam", "peran") else "w")
        self.tree_anggota.pack(fill="both", expand=True)

        self.lbl_total = ttk.Label(frame, text="")
        self.lbl_total.pack(anchor="w", pady=(4, 0))

        form = ttk.LabelFrame(frame, text="Daftar Anggota Baru", padding=10)
        form.pack(fill="x", pady=(6, 0))
        self.var_nama = tk.StringVar()
        self.var_id = tk.StringVar()
        self.var_peran = tk.StringVar(value="Mahasiswa")
        self.var_ket = tk.StringVar()

        ttk.Label(form, text="Nama").grid(row=0, column=0, sticky="w", padx=4)
        ttk.Entry(form, textvariable=self.var_nama, width=26).grid(row=1, column=0, padx=4)
        ttk.Label(form, text="ID Anggota").grid(row=0, column=1, sticky="w", padx=4)
        ttk.Entry(form, textvariable=self.var_id, width=16).grid(row=1, column=1, padx=4)
        ttk.Label(form, text="Peran").grid(row=0, column=2, sticky="w", padx=4)
        cb = ttk.Combobox(form, textvariable=self.var_peran, state="readonly",
                          values=["Mahasiswa", "Dosen"], width=12)
        cb.grid(row=1, column=2, padx=4)
        cb.bind("<<ComboboxSelected>>", self._ganti_peran)
        self.lbl_ket = ttk.Label(form, text="Jurusan")
        self.lbl_ket.grid(row=0, column=3, sticky="w", padx=4)
        ttk.Entry(form, textvariable=self.var_ket, width=26).grid(row=1, column=3, padx=4)
        ttk.Button(form, text="Daftarkan",
                   command=self.aksi_daftar_anggota).grid(row=1, column=4, padx=10)

    def _ganti_peran(self, _event=None):
        self.lbl_ket.config(
            text="Jurusan" if self.var_peran.get() == "Mahasiswa" else "Mata Kuliah")

    def aksi_daftar_anggota(self):
        nama = self.var_nama.get().strip()
        id_anggota = self.var_id.get().strip()
        ket = self.var_ket.get().strip()
        try:
            if not (nama and id_anggota and ket):
                raise ValueError("Nama, ID, dan jurusan/mata kuliah wajib diisi")
            kelas = Mahasiswa if self.var_peran.get() == "Mahasiswa" else Dosen
            self.perpus.daftarkan_anggota(kelas(nama, id_anggota, ket))
        except ValueError as e:
            self._error(e)
            return
        for v in (self.var_nama, self.var_id, self.var_ket):
            v.set("")
        self._sukses(f"Anggota '{nama}' berhasil didaftarkan")

    # ------------------------------------------------------------
    # TAB 3 : PEMINJAMAN & PENGEMBALIAN
    # ------------------------------------------------------------
    def _buat_tab_pinjam(self):
        frame = ttk.Frame(self.tab, padding=10)
        self.tab.add(frame, text="  Peminjaman & Pengembalian  ")

        atas = ttk.LabelFrame(frame, text="1. Pilih Anggota", padding=10)
        atas.pack(fill="x")
        self.var_pilih_anggota = tk.StringVar()
        self.cb_anggota = ttk.Combobox(atas, textvariable=self.var_pilih_anggota,
                                       state="readonly", width=60)
        self.cb_anggota.pack(side="left")
        self.cb_anggota.bind("<<ComboboxSelected>>", lambda e: self.refresh_pinjaman())
        self.lbl_info = ttk.Label(atas, text="")
        self.lbl_info.pack(side="left", padx=12)

        bawah = ttk.Frame(frame)
        bawah.pack(fill="both", expand=True, pady=(10, 0))

        kiri = ttk.LabelFrame(bawah, text="2. Pinjam Buku", padding=10)
        kiri.pack(side="left", fill="both", expand=True, padx=(0, 6))
        ttk.Label(kiri, text="Pilih buku (kode - judul):").pack(anchor="w")
        self.var_pilih_buku = tk.StringVar()
        self.cb_buku = ttk.Combobox(kiri, textvariable=self.var_pilih_buku,
                                    state="readonly", width=46)
        self.cb_buku.pack(anchor="w", pady=6)
        ttk.Button(kiri, text="📖  Pinjam Buku",
                   command=self.aksi_pinjam).pack(anchor="w", pady=6)

        kanan = ttk.LabelFrame(bawah, text="3. Buku yang Sedang Dipinjam (pilih untuk dikembalikan)",
                               padding=10)
        kanan.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self.tree_pinjam = ttk.Treeview(kanan, columns=("kode", "judul"),
                                        show="headings", height=6, selectmode="browse")
        self.tree_pinjam.heading("kode", text="Kode")
        self.tree_pinjam.heading("judul", text="Judul Buku")
        self.tree_pinjam.column("kode", width=70, anchor="center")
        self.tree_pinjam.column("judul", width=250)
        self.tree_pinjam.pack(fill="both", expand=True)
        ttk.Button(kanan, text="↩  Kembalikan Buku Terpilih",
                   command=self.aksi_kembali).pack(anchor="w", pady=(8, 0))

    def _anggota_terpilih(self):
        teks = self.var_pilih_anggota.get()
        if not teks:
            raise ValueError("Pilih anggota terlebih dahulu")
        return teks.split(" - ")[0]          # format: "ID - Nama (Peran)"

    def aksi_pinjam(self):
        try:
            id_anggota = self._anggota_terpilih()
            teks = self.var_pilih_buku.get()
            if not teks:
                raise ValueError("Pilih buku terlebih dahulu")
            kode = teks.split(" - ")[0]      # format: "KODE - Judul (stok n)"
            pesan = self.perpus.pinjam_buku(id_anggota, kode)
        except ValueError as e:
            self._error(e)
            return
        self.var_pilih_buku.set("")
        self._sukses(pesan)

    def aksi_kembali(self):
        try:
            id_anggota = self._anggota_terpilih()
            pilihan = self.tree_pinjam.selection()
            if not pilihan:
                raise ValueError("Pilih buku yang akan dikembalikan pada tabel")
            kode = self.tree_pinjam.item(pilihan[0], "values")[0]
            pesan = self.perpus.kembalikan_buku(id_anggota, kode)
        except ValueError as e:
            self._error(e)
            return
        self._sukses(pesan)

    # ------------------------------------------------------------
    # REFRESH TAMPILAN
    # ------------------------------------------------------------
    def refresh_semua(self):
        # tabel buku
        self.tree_buku.delete(*self.tree_buku.get_children())
        for b in self.perpus.daftar_buku():
            status = "Tersedia" if b.tersedia else "Habis"
            self.tree_buku.insert("", "end", tags=("" if b.tersedia else "habis",),
                                  values=(b.kode, b.judul, b.penulis, b.stok, status))

        # tabel anggota
        self.tree_anggota.delete(*self.tree_anggota.get_children())
        for a in self.perpus.daftar_anggota():
            self.tree_anggota.insert("", "end", values=(
                a.id_anggota, a.nama, a.peran(), a.keterangan(),
                a.batas_pinjam(), len(a.daftar_pinjaman)))
        self.lbl_total.config(text=f"Total anggota terdaftar: {Anggota.total_anggota()}")

        # pilihan combobox (pilihan lama dipertahankan bila masih ada)
        daftar_a = [f"{a.id_anggota} - {a.nama} ({a.peran()})"
                    for a in self.perpus.daftar_anggota()]
        daftar_b = [f"{b.kode} - {b.judul} (stok {b.stok})"
                    for b in self.perpus.daftar_buku()]
        self.cb_anggota["values"] = daftar_a
        self.cb_buku["values"] = daftar_b
        if self.var_pilih_anggota.get() not in daftar_a:
            self.var_pilih_anggota.set("")
        if self.var_pilih_buku.get() not in daftar_b:
            self.var_pilih_buku.set("")
        self.refresh_pinjaman()

    def refresh_pinjaman(self):
        self.tree_pinjam.delete(*self.tree_pinjam.get_children())
        teks = self.var_pilih_anggota.get()
        if not teks:
            self.lbl_info.config(text="")
            return
        anggota = self.perpus.cari_anggota(teks.split(" - ")[0])
        for b in anggota.daftar_pinjaman:
            self.tree_pinjam.insert("", "end", values=(b.kode, b.judul))
        self.lbl_info.config(
            text=f"Dipinjam: {len(anggota.daftar_pinjaman)} / {anggota.batas_pinjam()} buku")

    # ------------------------------------------------------------
    # PESAN
    # ------------------------------------------------------------
    def _sukses(self, pesan):
        self.status.set(pesan)
        messagebox.showinfo("Berhasil", pesan)
        self.refresh_semua()

    def _error(self, e):
        self.status.set(f"Error: {e}")
        messagebox.showerror("Gagal", str(e))


# ===============================================================
#  PROGRAM UTAMA
# ===============================================================
if __name__ == "__main__":
    perpus = Perpustakaan("Perpustakaan Universitas Bina Bangsa")
    isi_data_awal(perpus)
    AplikasiPerpustakaan(perpus).mainloop()