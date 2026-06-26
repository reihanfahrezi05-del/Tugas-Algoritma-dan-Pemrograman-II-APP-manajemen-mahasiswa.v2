import streamlit as st
import json
import re
import os


FILE_NAME = "mahasiswa.json"

st.set_page_config(
    page_title="Manajemen Mahasiswa",
    layout="centered"
)


class Person:
    def __init__(self, nama):
        self._nama = nama

class Mahasiswa(Person):
    def __init__(self, nim, nama, ipk):
        super().__init__(nama)
        self.__nim = nim
        self.__ipk = ipk

    def get_nim(self):
        return self.__nim

    def get_nama(self):
        return self._nama

    def get_ipk(self):
        return self.__ipk
        
    def to_dict(self):
        return {"nim": self.__nim, "nama": self._nama, "ipk": self.__ipk}

    @classmethod
    def from_dict(cls, data):
        return cls(nim=data["nim"], nama=data["nama"], ipk=data["ipk"])


def load_data():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as file:
                raw_data = json.load(file)
                return [Mahasiswa.from_dict(item) for item in raw_data]
        except:
            st.error("Error baca data JSON. Mulai dari awal.")
            return []
    return []

def save_data(data):
    dict_data = [mhs.to_dict() for mhs in data]
    with open(FILE_NAME, "w") as file:
        json.dump(dict_data, file, indent=4)

def bubble_sort(data):
    n = len(data)
    for i in range(n):
        for j in range(0, n - i - 1):
            if data[j].get_nim() > data[j + 1].get_nim():
                data[j], data[j + 1] = data[j + 1], data[j]
    return data

def linear_search(data, nim):
    for item in data:
        if item.get_nim() == nim:
            return item
    return None

def is_nim_exist(data, nim):
    return linear_search(data, nim) is not None


# --- APP LOGIC ---

st.title("Tugas Manajemen Data Mahasiswa")

menu = st.sidebar.selectbox(
    "Pilih Menu",
    ["Tambah Data", "Lihat Data", "Cari Data", "Edit & Hapus Data", "Urutkan Data"]
)

data = load_data()

if menu == "Tambah Data":
    st.subheader("Tambah Mahasiswa Baru")
    
    nim = st.text_input("NIM")
    nama = st.text_input("Nama")
    ipk = st.number_input("IPK", min_value=0.0, max_value=4.0, step=0.01)

    if st.button("Simpan"):
        try:
            if not re.match(r'^\d{5}$', nim):
                raise Exception("NIM harus 5 digit angka")
            if is_nim_exist(data, nim):
                raise Exception("NIM sudah terdaftar!")
            if not nama.strip():
                raise Exception("Nama tidak boleh kosong")
            
            mhs_baru = Mahasiswa(nim=nim, nama=nama.strip(), ipk=ipk)
            data.append(mhs_baru)
            save_data(data)
            
            st.success("Data berhasil disimpan!")
            
        except Exception as e:
            st.error(str(e))

elif menu == "Lihat Data":
    st.subheader("Daftar Mahasiswa")
    
    if len(data) == 0:
        st.warning("Belum ada data.")
    else:
        df_data = [mhs.to_dict() for mhs in data]
        st.dataframe(df_data)

elif menu == "Cari Data":
    st.subheader("Cari Mahasiswa")
    cari = st.text_input("Masukkan NIM")
    
    if st.button("Cari"):
        hasil = linear_search(data, cari)
        if hasil:
            st.success("Data ditemukan!")
            st.write(f"NIM: {hasil.get_nim()}")
            st.write(f"Nama: {hasil.get_nama()}")
            st.write(f"IPK: {hasil.get_ipk()}")
        else:
            st.error("Data tidak ditemukan.")

elif menu == "Edit & Hapus Data":
    st.subheader("Update / Delete Mahasiswa")
    
    if len(data) == 0:
        st.warning("Belum ada data.")
    else:
        nim_edit = st.selectbox("Pilih Data (NIM):", [mhs.get_nim() for mhs in data])
        target = linear_search(data, nim_edit)
        
        if target:
            new_nama = st.text_input("Nama", value=target.get_nama())
            new_ipk = st.number_input("IPK", min_value=0.0, max_value=4.0, step=0.01, value=target.get_ipk())
            
            if st.button("Update"):
                if not new_nama.strip():
                    st.error("Nama tidak boleh kosong")
                else:
                    data = [m for m in data if m.get_nim() != target.get_nim()]
                    data.append(Mahasiswa(target.get_nim(), new_nama.strip(), new_ipk))
                    save_data(data)
                    st.success("Data diupdate!")
            
            if st.button("Hapus"):
                data = [m for m in data if m.get_nim() != target.get_nim()]
                save_data(data)
                st.success("Data dihapus!")
                st.rerun()

elif menu == "Urutkan Data":
    st.subheader("Sorting Mahasiswa")
    
    if st.button("Urutkan Berdasarkan NIM"):
        data = bubble_sort(data)
        save_data(data)
        st.success("Data berhasil diurutkan!")
        df_data = [mhs.to_dict() for mhs in data]
        st.dataframe(df_data)