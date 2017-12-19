from pymatgen import MPRester
from pylab import plot,show, scatter
import numpy as np
from pymatgen.symmetry.bandstructure import HighSymmKpath

from analytical_band_from_BZT import get_energy
from pymatgen import Spin
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from tools import get_energy_args, calc_analytical_energy, norm, \
    get_bindex_bspin, get_bs_extrema
from constants import hbar, m_e, Ry_to_eV, A_to_m, m_to_cm, A_to_nm, e, k_B,\
                        epsilon_0, default_small_E, dTdz, sq3

api = MPRester("fDJKEZpxSyvsXdCt")

def retrieve_bs(coeff_file, bs, ibands):
    # sp=bs.bands.keys()[0]
    engre, nwave, nsym, nstv, vec, vec2, out_vec2, br_dir = get_energy_args(coeff_file, ibands)

    #you can use a for loop along a certain list of k-points.
    for i, iband in enumerate(ibands):
        en = []
        sym_line_kpoints = [k.frac_coords for k in bs.kpoints]
        for kpt in sym_line_kpoints:
            # cbm = False
            cbm = True
            e, v, m = get_energy(kpt, engre[i], nwave, nsym, nstv, vec, vec2=vec2, out_vec2=out_vec2, br_dir=br_dir, cbm=cbm)
            en.append(e*13.605)

        # plot(np.array(bs.bands[sp])[iband-1,:].T-bs.efermi) # from MP
        # plot(np.array(bs.bands[sp])[iband-2,:].T-bs.efermi) # from MP
        # plot(np.array(bs.bands[sp])[iband-3,:].T-bs.efermi) # from MP
        plot(en, color='b') # interpolated by BoltzTraP
    show()




if __name__ == "__main__":
    # user inputs
    PbTe_id = 'mp-19717' # valence_idx = 9
    Si_id = 'mp-149' # valence_idx = 4
    GaAs_id = 'mp-2534' # valence_idx = 14
    SnSe2_id = "mp-665"

    bs = api.get_bandstructure_by_material_id(SnSe2_id)
    GaAs_st = api.get_structure_by_material_id(GaAs_id)
    bs.structure =  GaAs_st
    print(bs.get_sym_eq_kpoints([0.5, 0.5, 0.5]))

    vbm_idx = bs.get_vbm()['band_index'][Spin.up][0]
    ibands = [1, 2] # in this notation, 1 is the last valence band
    ibands = [i + vbm_idx + 1 for i in ibands]

    PbTe_coeff_file = '../test_files/PbTe/fort.123'
    Si_coeff_file = "../test_files/Si/Si_fort.123"
#    GaAs_coeff_file = "../test_files/GaAs/fort.123_GaAs_sym_23x23x23"
    GaAs_coeff_file = "../test_files/GaAs/fort.123_GaAs_1099kp"
    # SnSe2_coeff_file = "/Users/alirezafaghaninia/Dropbox/Berkeley_Lab_Work/Yanzhong_Pei/SnSe2/boltztrap_vdw_dense/boltztrap/fort.123"
    # SnSe2_coeff_file = "/Users/alirezafaghaninia/Documents/boltztrap_examples/SnSe2/boltztrap_vdw_soc/boltztrap/fort.123"
    # SnSe2_coeff_file = "/Users/alirezafaghaninia/Documents/boltztrap_examples/SnSe2/boltztrap_vdw_better_geom_dense/boltztrap/fort.123"

    # retrieve_bs(coeff_file=PbTe_coeff_file, bs=bs, ibands=ibands)

    # retrieve_bs(coeff_file=GaAs_coeff_file, bs=bs, ibands=ibands)

    # retrieve_bs(coeff_file=SnSe2_coeff_file, bs=bs, ibands=[11, 12, 13, 14])
    # retrieve_bs(coeff_file=SnSe2_coeff_file, bs=bs, ibands=[24, 25, 26, 27])

    extrema = get_bs_extrema(bs, coeff_file=GaAs_coeff_file, nk_ibz=17, v_cut=1e4, min_normdiff=0.1,
                   Ecut=0.5, nex_max=20)
    print(extrema)


    # if False:
    #     ibz = HighSymmKpath(GaAs_st)
    #     print ibz.kpath
    #     sg = SpacegroupAnalyzer(GaAs_st)
    #     nk = 17
    #     v_cut = 10000
    #     norm_diff_cut = 0.05
    #     Ecut = 1.2
    #     kpts = [k_n_w[0] for k_n_w in sg.get_ir_reciprocal_mesh(mesh=(nk, nk, nk))]
    #     kpts.extend(ibz.kpath['kpoints'].values())
    #     grid = {'energy': [], 'velocity': [], 'mass': []}
    #     engre, nwave, nsym, nstv, vec, vec2, out_vec2, br_dir = get_energy_args(coeff_file=GaAs_coeff_file, ibands=ibands)
    #     # print kpts
    #     cbm = True
    #
    #     for iband in range(len(ibands)):
    #         if iband == 0:
    #             cbm = False
    #         else:
    #             cbm = True
    #         print('for the band {}'.format(ibands[iband]))
    #         energies = []
    #         velocities = []
    #         normv = []
    #         masses = []
    #         for ik, kpt in enumerate(kpts):
    #             sgn = 1
    #             en, v, mass = calc_analytical_energy(kpt, engre[iband], nwave, nsym, nstv, vec, vec2, out_vec2,
    #                 br_dir, sgn, scissor=0)
    #             # en, v, mass = get_energy(kpt, engre[iband], nwave, nsym, nstv, vec,
    #             #                      vec2=vec2, out_vec2=out_vec2, br_dir=br_dir,
    #             #                      cbm=True)
    #             energies.append(en)
    #             velocities.append(abs(v))
    #             normv.append(norm(v))
    #             masses.append(mass.trace()/3)
    #
    #         indexes = np.argsort(normv)[:20]
    #         energies = [energies[i] for i in indexes]
    #         if cbm:
    #             extremum0 = min(energies) # extremum0 is CBM here
    #         else:
    #             extremum0 = max(energies)
    #         print ('extremum0: {}'.format(extremum0))
    #         normv = [normv[i] for i in indexes]
    #         velocities = [velocities[i] for i in indexes]
    #         masses = [masses[i] for i in indexes]
    #         kpts = [kpts[i] for i in indexes]
    #
    #         print ('\nhere')
    #         print normv
    #         print kpts
    #         print
    #         # if (velocities[0] <= v_cut).any():
    #         # if normv[0] <= v_cut:
    #         #     extrema = [kpts[0]]
    #         # else:
    #         extrema = []
    #         if normv[0] > v_cut:
    #             raise ValueError('No extremum point (v<{}) found!'.format(v_cut))
    #         for i in range(0, len(kpts)):
    #             # if (velocities[i] > v_cut).all() :
    #             if normv[i] > v_cut:
    #                 break
    #             else:
    #                 far_enough = True
    #                 for k in extrema:
    #                     if norm(kpts[i] - k) <= norm_diff_cut:
    #                         far_enough = False
    #                 if far_enough \
    #                         and abs(energies[i]-extremum0) < Ecut \
    #                         and masses[i]*(-1)**(int(cbm)+1)>=0:
    #                     extrema.append(kpts[i])
    #
    #         print('extrema:')
    #         print extrema
    #
