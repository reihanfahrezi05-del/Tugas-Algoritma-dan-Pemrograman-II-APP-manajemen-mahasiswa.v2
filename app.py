import streamlit as st
import json
import re
import os


FILE_NAME = "mahasiswa.json"

# UI Configuration (Gamified / Duolingo Style)
st.set_page_config(
    page_title="Akademi Mahasiswa",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Duolingo color palette and styling */
    .stApp {
        background-color: #F7F9FC;
    }
    h1, h2, h3 {
        color: #58CC02;
        font-family: 'Comic Sans MS', 'Nunito', sans-serif;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #58CC02;
        color: white;
        border-radius: 16px;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 0 #58A700;
        transition: all 0.1s;
    }
    .stButton>button:active {
        transform: translateY(4px);
        box-shadow: 0 0 0 #58A700;
    }
    div[data-baseweb="input"] > div {
        border-radius: 12px;
        border: 2px solid #E5E5E5;
        background-color: white;
    }
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        border: 2px solid #E5E5E5;
        text-align: center;
        box-shadow: 0 4px 0 #E5E5E5;
    }
    .sidebar-header {
        font-size: 24px;
        font-weight: bold;
        color: #CE82FF;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


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
                # Convert raw JSON dicts to Mahasiswa objects
                return [Mahasiswa.from_dict(item) for item in raw_data]
        except (json.JSONDecodeError, KeyError):
            st.error("⚠️ File JSON rusak! Memulai database baru.")
            return []
    return []

def save_data(data):
    # Convert Mahasiswa objects to dicts for JSON
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

st.sidebar.markdown('<div class="sidebar-header">🎒 Misi Hari Ini</div>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Pilih Misi:",
    ["🌟 Rekrut Siswa Baru", "📖 Buku Daftar Siswa", "🔍 Lacak Siswa", "⚙️ Edit & Hapus", "🏆 Ranking (Sort)"]
)

data = load_data()

st.title("🎓 Akademi Master Data")

if menu == "🌟 Rekrut Siswa Baru":
    st.header("📝 Formulir Pendaftaran")
    st.markdown("Isi data dengan benar untuk mendapatkan XP!")
    
    col1, col2 = st.columns(2)
    with col1:
        nim = st.text_input("💳 NIM (5 Digit Angka)", max_chars=5)
    with col2:
        nama = st.text_input("👤 Nama Lengkap Siswa")
        
    ipk = st.number_input("⭐ Skor IPK Awal", min_value=0.0, max_value=4.0, step=0.01)

    if st.button("🚀 Daftarkan Sekarang!"):
        try:
            if not re.match(r'^\d{5}$', nim):
                raise Exception("NIM harus tepat 5 digit angka!")
            if is_nim_exist(data, nim):
                raise Exception("Aduh! NIM ini sudah terdaftar. Gunakan NIM lain.")
            if not nama.strip():
                raise Exception("Nama tidak boleh kosong!")
            if ipk == 0.0:
                st.warning("Catatan: Mendaftar dengan IPK 0.0. Apakah kamu yakin? Tapi tetap disimpan.")
            
            # Create object and save
            mhs_baru = Mahasiswa(nim=nim, nama=nama.strip(), ipk=ipk)
            data.append(mhs_baru)
            save_data(data)
            
            st.success("🎉 Berhasil! Kamu dapat +50 XP! Siswa telah terdaftar.")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Misi Gagal: {str(e)}")

elif menu == "📖 Buku Daftar Siswa":
    st.header("📚 Siswa Terdaftar")
    
    if len(data) == 0:
        st.info("Krik krik... Akademi masih kosong. Ayo rekrut siswa!")
    else:
        # Konversi object back to dict buat visualisasi tabel
        df_data = [mhs.to_dict() for mhs in data]
        st.dataframe(df_data, use_container_width=True)
        
        st.markdown(f'<div class="metric-card"><h3>Total Siswa</h3><h1>{len(data)}</h1></div>', unsafe_allow_html=True)

elif menu == "🔍 Lacak Siswa":
    st.header("🕵️‍♂️ Mode Detektif")
    cari = st.text_input("🔍 Masukkan NIM Target (5 Digit)")
    
    if st.button("Cari Target!"):
        if not re.match(r'^\d{5}$', cari):
            st.error("NIM harus 5 digit angka bro!")
        else:
            hasil = linear_search(data, cari)
            if hasil:
                st.success("🎯 Target Ditemukan!")
                col1, col2, col3 = st.columns(3)
                col1.metric("NIM", hasil.get_nim())
                col2.metric("Nama", hasil.get_nama())
                col3.metric("IPK", hasil.get_ipk())
            else:
                st.error("👻 Siswa menghilang! Data tidak ditemukan.")

elif menu == "⚙️ Edit & Hapus":
    st.header("🛠️ Bengkel Data")
    
    if len(data) == 0:
        st.info("Belum ada data untuk diedit.")
    else:
        nim_edit = st.selectbox("Pilih Siswa (Berdasarkan NIM):", [mhs.get_nim() for mhs in data])
        target = linear_search(data, nim_edit)
        
        if target:
            st.markdown("### Update Data")
            new_nama = st.text_input("Nama Baru", value=target.get_nama())
            new_ipk = st.number_input("IPK Baru", min_value=0.0, max_value=4.0, step=0.01, value=target.get_ipk())
            
            col_u, col_d = st.columns(2)
            with col_u:
                if st.button("💾 Simpan Perubahan"):
                    if not new_nama.strip():
                        st.error("Nama tidak boleh kosong!")
                    else:
                        # Update data (manual hapus lalu insert object baru, krn private attr)
                        data = [m for m in data if m.get_nim() != target.get_nim()]
                        data.append(Mahasiswa(target.get_nim(), new_nama.strip(), new_ipk))
                        save_data(data)
                        st.success("✨ Data berhasil di-upgrade! +20 XP")
            
            with col_d:
                if st.button("🧨 Hapus Data (Drop out)"):
                    data = [m for m in data if m.get_nim() != target.get_nim()]
                    save_data(data)
                    st.success("🔥 Data dihapus! Sayonara.")
                    st.rerun()

elif menu == "🏆 Ranking (Sort)":
    st.header("📊 Papan Peringkat (Berdasarkan NIM)")
    st.markdown("Bubble Sort bekerja di balik layar...")
    
    if st.button("Urutkan Data Sekarang!"):
        if len(data) < 2:
            st.info("Data kurang dari 2. Tidak perlu diurutkan.")
        else:
            data = bubble_sort(data)
            save_data(data)
            st.success("🔀 Sorting Selesai! XP +10")
            df_data = [mhs.to_dict() for mhs in data]
            st.dataframe(df_data, use_container_width=True)