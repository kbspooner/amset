import re
from pathlib import Path

import click
from click import argument, option

__author__ = "Alex Ganose"
__maintainer__ = "Alex Ganose"
__email__ = "aganose@lbl.gov"

from amset.tools.common import image_type, path_type, zero_weighted_type

kpaths = click.Choice(["pymatgen", "seekpath"], case_sensitive=False)
x_properties = click.Choice(["doping", "temperature"], case_sensitive=False)
rate_plot_type = click.Choice(
    ["rate", "lifetime", "v2tau", "v2taudfde"], case_sensitive=False
)

_symprec = 0.01  # redefine symprec to avoid loading constants from file
_dos_estep = 0.01  # redefine symprec to avoid loading constants from file
_interpolation_factor = 5


def _all_or_int(value):
    if value == "all":
        return None
    elif value is None:
        return 0
    else:
        return int(value)


def _parse_kpoints(kpoints):
    return [
        [list(map(float, kpt.split())) for kpt in kpts.split(",")]
        for kpts in kpoints.split("|")
    ]


def _parse_kpoint_labels(labels):
    return [path.split(",") for path in labels.split("|")]


@click.group()
def plot():
    """
    Plot AMSET results, including scattering rates and band structures
    """
    pass


@plot.command()
@argument("filename", type=path_type)
@option("-t", "--temperature", default=0, help="temperature index [default: 0]")
@option("-d", "--doping", default=0, help="doping index [default: 0]")
@option("-l", "--line-density", default=100.0, help="band structure line density")
@option("-p", "--prefix", help="output filename prefix")
@option("--emin", help="minimum energy limit", type=float)
@option("--emax", help="maximum energy limit", type=float)
@option(
    "--amin",
    default=5e-5,
    help="minimum spectral weight for normalizing linewidth in 1/meV",
)
@option(
    "--amax",
    default=1e-1,
    help="maximum spectral weight for normalizing linewidth in 1/meV",
)
@option("--cmap", default="viridis", help="matplotlib colormap to use")
@option("--no-colorbar", default=True, is_flag=True, help="don't add a colorbar")
@option("--symprec", type=float, default=_symprec, help="interpolation factor")
@option("--kpath", type=kpaths, help="k-point path type")
@option(
    "--kpoints",
    type=_parse_kpoints,
    metavar="K",
    help="manual k-points list [e.g. '0 0 0, 0.5 0 0']",
)
@option(
    "--labels",
    type=_parse_kpoint_labels,
    metavar="L",
    help=r"labels for manual kpoints [e.g. '\Gamma,X']",
)
@option("--interpolation-factor", default=1, help="BoltzTraP interpolation factor")
@option("--width", default=3.2, help="figure width [default: 6]")
@option("--height", default=3.2, help="figure height [default: 6]")
@option("--directory", type=path_type, help="file output directory")
@option("--format", "image_format", default="pdf", type=image_type, help="image format")
@option("--style", help="matplotlib style specification")
@option("--no-base-style", default=False, is_flag=True, help="don't apply base style")
def lineshape(filename, **kwargs):
    """
    Plot band structures with electron lineshape
    """
    from amset.plot.lineshape import LineshapePlotter

    plotter = LineshapePlotter(
        filename, print_log=True, interpolation_factor=kwargs["interpolation_factor"]
    )

    kpath = get_kpath(
        plotter.structure,
        mode=kwargs["kpath"],
        symprec=kwargs["symprec"],
        kpt_list=kwargs["kpoints"],
        labels=kwargs["labels"],
    )

    plt = plotter.get_plot(
        kwargs["doping"],
        kwargs["temperature"],
        line_density=kwargs["line_density"],
        emin=kwargs["emin"],
        emax=kwargs["emax"],
        amin=kwargs["amin"],
        amax=kwargs["amax"],
        cmap=kwargs["cmap"],
        colorbar=kwargs["no_colorbar"],
        width=kwargs["width"],
        height=kwargs["height"],
        style=kwargs["style"],
        no_base_style=kwargs["no_base_style"],
        kpath=kpath,
    )

    save_plot(
        plt, "lineshape", kwargs["directory"], kwargs["prefix"], kwargs["image_format"]
    )
    return plt


@plot.command()
@argument("filename", type=path_type)
@option("-l", "--line-density", default=100.0, help="band structure line density")
@option("--emin", default=-6.0, help="minimum energy limit")
@option("--emax", default=6.0, help="maximum energy limit")
@option("--symprec", type=float, default=_symprec, help="interpolation factor")
@option("--print-log/--no-print-log", default=True, help="whether to print interpolation log")
@option("--kpath", type=kpaths, help="k-point path type")
@option(
    "--kpoints",
    type=_parse_kpoints,
    metavar="K",
    help="manual k-points list [e.g. '0 0 0, 0.5 0 0']",
)
@option(
    "--labels",
    type=_parse_kpoint_labels,
    metavar="L",
    help=r"labels for manual kpoints [e.g. '\Gamma,X']",
)
@option(
    "--interpolation-factor",
    default=_interpolation_factor,
    type=float,
    help="BoltzTraP interpolation factor",
)
@option("--energy-cutoff", type=float, help="interpolation energy cutoff in eV")
@option(
    "-z",
    "--zero-weighted-kpoints",
    help="how to process zero-weighted k-points",
    type=zero_weighted_type,
)
@option("--plot-dos", is_flag=True, help="whether to also plot the density of states")
@option(
    "--dos-kpoints",
    default="50",
    help="k-point length cutoff or mesh for density of states",
)
@option("--dos-estep", default=_dos_estep, help="dos energy step size")
@option("--dos-aspect", default=3.0, help="aspect ratio for the density of states")
@option(
    "--no-zero-to-efermi",
    "zero_to_efermi",
    is_flag=True,
    default=True,
    help="don't set the Fermi level to zero",
)
@option("--vbm-cbm-marker", is_flag=True, help="add a marker at the CBM and VBM")
@option("--width", default=6.0, help="figure width [default: 6]")
@option("--height", default=6.0, help="figure height [default: 6]")
@option("-p", "--prefix", help="output filename prefix")
@option("--directory", type=path_type, help="file output directory")
@option("--format", "image_format", default="pdf", type=image_type, help="image format")
@option("--style", help="path to matplotlib style specification")
@option("--no-base-style", default=False, is_flag=True, help="don't apply base style")
def band(filename, **kwargs):
    """
    Plot interpolate band structure from vasprun file
    """
    from amset.constants import defaults
    from amset.plot.electronic_structure import ElectronicStructurePlotter

    zwk_mode = kwargs.pop("zero_weighted_kpoints")
    if not zwk_mode:
        zwk_mode = defaults["zero_weighted_kpoints"]

    plotter_kwargs = {
        "print_log": kwargs["print_log"],
        "interpolation_factor": kwargs["interpolation_factor"],
        "symprec": kwargs["symprec"],
        "energy_cutoff": kwargs["energy_cutoff"],
    }
    if not is_vasprun_file(filename):
        click.Abort("Unrecognised filetype, expecting a vasprun.xml file.")

    plotter = ElectronicStructurePlotter.from_vasprun(
        filename, zero_weighted_kpoints=zwk_mode, **plotter_kwargs
    )
    kpath = get_kpath(
        plotter.structure,
        mode=kwargs["kpath"],
        symprec=kwargs["symprec"],
        kpt_list=kwargs["kpoints"],
        labels=kwargs["labels"],
    )

    dos_kpoints = _get_dos_kpoints(plotter.structure, kwargs["dos_kpoints"])

    plt = plotter.get_plot(
        plot_band_structure=True,
        plot_dos=kwargs["plot_dos"],
        line_density=kwargs["line_density"],
        dos_kpoints=dos_kpoints,
        dos_estep=kwargs["dos_estep"],
        dos_aspect=kwargs["dos_aspect"],
        zero_to_efermi=kwargs["zero_to_efermi"],
        vbm_cbm_marker=kwargs["vbm_cbm_marker"],
        emin=kwargs["emin"],
        emax=kwargs["emax"],
        width=kwargs["width"],
        height=kwargs["height"],
        style=kwargs["style"],
        no_base_style=kwargs["no_base_style"],
        kpath=kpath,
    )

    save_plot(
        plt, "band", kwargs["directory"], kwargs["prefix"], kwargs["image_format"]
    )
    return plt


@plot.command()
@argument("filename", type=path_type)
@option("-d", "--doping-idx", metavar="N", help="doping index to plot")
@option("-t", "--temperature-idx", metavar="N", help="temperature index to plot")
@option(
    "-s",
    "--separate-rates",
    is_flag=True,
    default=False,
    help="whether to separate scattering mechanisms",
)
@option(
    "--plot-type",
    type=rate_plot_type,
    default="rate",
    help="what to plot on the y-axis",
)
@option(
    "--total/--no-total", "plot_total_rate", default=False, help="plot the total rate"
)
@option(
    "--dfde/--no-dfde",
    "show_dfde",
    default=False,
    help="indicate the Fermi-Dirac derivative weight through color saturation",
)
@option("--use-symbol/--no-use-symbol", default=False, help="use symbols for labels")
@option(
    "--fd-tols/--no-fd-tols",
    "plot_fd_tols",
    default=False,
    help="plot the Fermi-Dirac tolerance limits",
)
@option(
    "--normalize/--no-normalize",
    "normalize_energy",
    default=True,
    help="normalize energies to the VBM/Fermi level",
)
@option("--pad", type=float, default=0.1, help="pad in % for y-axis limits")
@option("--ymin", default=None, type=float, help="minimum y-axis limit")
@option("--ymax", default=None, type=float, help="maximum y-axis limit")
@option("--xmin", default=None, type=float, help="minimum x-axis limit")
@option("--xmax", default=None, type=float, help="maximum x-axis limit")
@option("--total-color", help="color for total scattering rate")
@option("-p", "--prefix", help="output filename prefix")
@option("--directory", type=path_type, help="file output directory")
@option("--format", "image_format", default="pdf", type=image_type, help="image format")
@option("--style", help="path to matplotlib style specification")
@option("--no-base-style", default=False, is_flag=True, help="don't apply base style")
@option("--font", "fonts", help="font to use")
def rates(filename, **kwargs):
    """
    Plot scattering rates
    """
    from amset.plot.rates import RatesPlotter

    save_kwargs = [kwargs.pop(d) for d in ["directory", "prefix", "image_format"]]

    kwargs["doping_idx"] = _all_or_int(kwargs["doping_idx"])
    kwargs["temperature_idx"] = _all_or_int(kwargs["temperature_idx"])

    pad = kwargs.pop("pad")
    use_symbol = kwargs.pop("use_symbol")
    plotter = RatesPlotter(filename, pad=pad, use_symbol=use_symbol)
    plt = plotter.get_plot(**kwargs)
    plt.subplots_adjust(hspace=0.3, wspace=0.4)
    save_plot(plt, "rates", *save_kwargs)
    return plt


@plot.command()
@argument("filename", type=path_type)
@option(
    "-d", "--doping-idx", metavar="N", help="doping indices to plot (space separated)"
)
@option(
    "-t",
    "--temperature-idx",
    metavar="N",
    help="temperature indices to plot (space separated)",
)
@option("-x", "--x-property", type=x_properties, help="property to plot on x-axis")
@option("--grid", nargs=2, type=int, help="subplot grid (nrows, ncols)")
@option(
    "--average/--no-average",
    default=True,
    help="whether to average tensor transport properties",
)
@option("--pad", type=float, default=0.05, help="pad in % for axis limits")
@option("--use-symbol/--no-use-symbol", default=False, help="use symbols for labels")
@option("--xlabel", help="x-axis label")
@option("--xmin", type=float, help="minimum x-axis limit")
@option("--xmax", type=float, help="maximum x-axis limit")
@option("--logx/--no-log-x", default=None, help="log x-axis")
@option("--conductivity/--no-conductivity", default=True, help="plot conductivity")
@option("--seebeck/--no-seebeck", default=True, help="plot Seebeck coefficient")
@option(
    "--thermal-conductivity/--no-thermal-conductivity",
    default=True,
    help="plot electronic thermal conductivity",
)
@option("--mobility/--no-mobility", default=False, help="plot electron mobility")
@option("--conductivity-label", help="conductivity y-axis label")
@option("--conductivity-min", type=float, help="minimum conductivity y-axis limit")
@option("--conductivity-max", type=float, help="maximum conductivity y-axis limit")
@option(
    "--log-conductivity/--no-log-conductivity",
    default=None,
    help="plot log conductivity",
)
@option("--seebeck-label", help="Seebeck coefficient y-axis label")
@option("--seebeck-min", type=float, help="minimum Seebeck y-axis limit")
@option("--seebeck-max", type=float, help="maximum Seebeck y-axis limit")
@option("--log-seebeck/--no-log-seebeck", default=None, help="plot log Seebeck")
@option("--thermal-conductivity-label", help="thermal conductivity y-axis label")
@option(
    "--thermal-conductivity-min",
    type=float,
    help="minimum thermal conductivity y-axis limit",
)
@option(
    "--thermal-conductivity-max",
    type=float,
    help="maximum thermal conductivity y-axis limit",
)
@option(
    "--log-thermal-conductivity/--no-log-thermal-conductivity",
    default=None,
    help="plot log thermal conductivity",
)
@option("--mobility-label", help="mobility y-axis label")
@option("--mobility-min", type=float, help="minimum mobility y-axis limit")
@option("--mobility-max", type=float, help="maximum mobility y-axis limit")
@option("--log-mobility/--no-log-mobility", default=None, help="plot log mobility")
@option("-p", "--prefix", help="output filename prefix")
@option("--width", type=float, help="figure width")
@option("--height", type=float, help="figure height")
@option("--directory", type=path_type, help="file output directory")
@option("--format", "image_format", default="pdf", type=image_type, help="image format")
@option("--style", help="path to matplotlib style specification")
@option("--no-base-style", default=False, is_flag=True, help="don't apply base style")
@option("--font", "fonts", help="font to use")
def transport(filename, **kwargs):
    """
    Plot transport properties
    """
    from amset.plot.transport import TransportPlotter

    save_kwargs = [kwargs.pop(d) for d in ("directory", "prefix", "image_format")]

    properties = []
    for prop in ("conductivity", "seebeck", "thermal_conductivity", "mobility"):
        if kwargs.pop(prop):
            properties.append(prop.replace("_", " "))

    kwargs["temperature_idx"] = _to_int(kwargs["temperature_idx"])
    kwargs["doping_idx"] = _to_int(kwargs["doping_idx"])

    pad = kwargs.pop("pad")
    use_symbol = kwargs.pop("use_symbol")
    average = kwargs.pop("average")
    plotter = TransportPlotter(
        filename, pad=pad, use_symbol=use_symbol, average=average
    )
    plt = plotter.get_plot(properties=properties, **kwargs)
    plt.subplots_adjust(hspace=0.3, wspace=0.4)
    save_plot(plt, "transport", *save_kwargs)
    return plt


@plot.command()
@argument("filename", type=path_type)
@option(
    "-d", "--doping-idx", metavar="N", help="doping indices to plot (space separated)"
)
@option(
    "-t",
    "--temperature-idx",
    metavar="N",
    help="temperature indices to plot (space separated)",
)
@option("-x", "--x-property", type=x_properties, help="property to plot on x-axis")
@option(
    "--separate-mobility/--no-separate-mobility",
    default=True,
    help="whether to separate mobility for each scattering mechanisms",
)
@option("--title/--no-title", default=True, help="put a title above each subplot")
@option("--grid", nargs=2, type=int, help="subplot grid (nrows, ncols)")
@option(
    "--average/--no-average",
    default=True,
    help="whether to average tensor transport properties",
)
@option("--pad", type=float, default=0.05, help="pad in % for axis limits")
@option("--use-symbol/--no-use-symbol", default=False, help="use symbols for labels")
@option("--xlabel", help="x-axis label")
@option("--xmin", type=float, help="minimum x-axis limit")
@option("--xmax", type=float, help="maximum x-axis limit")
@option("--logx/--no-log-x", default=None, help="log x-axis")
@option("--ylabel", help="y-axis label")
@option("--ymin", type=float, help="minimum y-axis limit")
@option("--ymax", type=float, help="maximum y-axis limit")
@option("--total-color", help="color for total mobility line")
@option("--logy/--no-log-y", default=None, help="log y-axis")
@option("-p", "--prefix", help="output filename prefix")
@option("--width", type=float, help="figure width")
@option("--height", type=float, help="figure height")
@option("--directory", type=path_type, help="file output directory")
@option("--format", "image_format", default="pdf", type=image_type, help="image format")
@option("--style", help="path to matplotlib style specification")
@option("--no-base-style", default=False, is_flag=True, help="don't apply base style")
@option("--font", "fonts", help="font to use")
def mobility(filename, **kwargs):
    """
    Plot mobility in more detail
    """
    from amset.plot.mobility import MobilityPlotter

    save_kwargs = [kwargs.pop(d) for d in ("directory", "prefix", "image_format")]

    kwargs["temperature_idx"] = _to_int(kwargs["temperature_idx"])
    kwargs["doping_idx"] = _to_int(kwargs["doping_idx"])

    init_kwargs = {
        d: kwargs.pop(d) for d in ["use_symbol", "average", "separate_mobility", "pad"]
    }
    plotter = MobilityPlotter(filename, **init_kwargs)
    plt = plotter.get_plot(**kwargs)
    plt.subplots_adjust(hspace=0.3, wspace=0.4)
    save_plot(plt, "mobility", *save_kwargs)
    return plt


@plot.command()
@argument("filenames", nargs=-1, type=path_type)
@option("-d", "--doping-idx", metavar="N", help="doping indices to plot")
@option("-t", "--temperature-idx", metavar="N", help="temperature indices to plot")
@option("-x", "--x-property", type=x_properties, help="property to plot on x-axis")
@option("--grid", nargs=2, type=int, help="subplot grid (nrows, ncols)")
@option("--pad", type=float, default=0.05, help="pad in % for axis limits")
@option("--labels", help="labels to use (space separated)")
@option("--use-symbol/--no-use-symbol", default=False, help="use symbols for labels")
@option("--xlabel", help="x-axis label")
@option("--xmin", type=float, help="minimum x-axis limit")
@option("--xmax", type=float, help="maximum x-axis limit")
@option("--logx/--no-log-x", default=None, help="log x-axis")
@option("--conductivity/--no-conductivity", default=True, help="plot conductivity")
@option("--seebeck/--no-seebeck", default=True, help="plot Seebeck coefficient")
@option(
    "--thermal-conductivity/--no-thermal-conductivity",
    default=True,
    help="plot electronic thermal conductivity",
)
@option("--mobility/--no-mobility", default=False, help="plot electron mobility")
@option("--conductivity-label", help="conductivity y-axis label")
@option("--conductivity-min", type=float, help="minimum conductivity y-axis limit")
@option("--conductivity-max", type=float, help="maximum conductivity y-axis limit")
@option(
    "--log-conductivity/--no-log-conductivity",
    default=None,
    help="plot log conductivity",
)
@option("--seebeck-label", help="Seebeck coefficient y-axis label")
@option("--seebeck-min", type=float, help="minimum Seebeck y-axis limit")
@option("--seebeck-max", type=float, help="maximum Seebeck y-axis limit")
@option("--log-seebeck/--no-log-seebeck", default=None, help="plot log Seebeck")
@option("--thermal-conductivity-label", help="thermal conductivity y-axis label")
@option(
    "--thermal-conductivity-min",
    type=float,
    help="minimum thermal conductivity y-axis limit",
)
@option(
    "--thermal-conductivity-max",
    type=float,
    help="maximum thermal conductivity y-axis limit",
)
@option(
    "--log-thermal-conductivity/--no-log-thermal-conductivity",
    default=None,
    help="plot log thermal conductivity",
)
@option("--mobility-label", help="mobility y-axis label")
@option("--mobility-min", type=float, help="minimum mobility y-axis limit")
@option("--mobility-max", type=float, help="maximum mobility y-axis limit")
@option("--log-mobility/--no-log-mobility", default=None, help="plot log mobility")
@option("-p", "--prefix", help="output filename prefix")
@option("--width", type=float, help="figure width")
@option("--height", type=float, help="figure height")
@option("--directory", type=path_type, help="file output directory")
@option("--format", "image_format", default="pdf", type=image_type, help="image format")
@option("--style", help="path to matplotlib style specification")
@option("--no-base-style", default=False, is_flag=True, help="don't apply base style")
@option("--font", "fonts", help="font to use")
def convergence(filenames, **kwargs):
    """
    Plot transport properties
    """
    from amset.plot.convergence import ConvergencePlotter

    save_kwargs = [kwargs.pop(d) for d in ("directory", "prefix", "image_format")]

    properties = []
    for prop in ("conductivity", "seebeck", "thermal_conductivity", "mobility"):
        if kwargs.pop(prop):
            properties.append(prop.replace("_", " "))

    if kwargs["labels"] is None:
        # try to determine labels from file names
        try:
            kwargs["labels"] = get_labels_from_filenames(filenames)
        except ValueError:
            click.echo("Could not determine labels from filenames. Use --labels option")

    kwargs["temperature_idx"] = _to_int(kwargs["temperature_idx"])
    kwargs["doping_idx"] = _to_int(kwargs["doping_idx"])

    pad = kwargs.pop("pad")
    use_symbol = kwargs.pop("use_symbol")
    plotter = ConvergencePlotter(filenames, pad=pad, use_symbol=use_symbol)
    plt = plotter.get_plot(properties=properties, **kwargs)
    plt.subplots_adjust(hspace=0.3, wspace=0.4)
    save_plot(plt, "convergence", *save_kwargs)
    return plt


def get_labels_from_filenames(filenames):
    labels = []
    for filename in filenames:
        match = re.search(r"\d+x\d+x\d+", str(filename))
        if not match:
            raise ValueError("Problem extracting mesh")
        labels.append(match[0])
    return labels


def _to_int(idxs):
    if idxs is not None:
        idxs = list(map(int, idxs.split()))
    return idxs


def save_plot(plt, name, directory, prefix, image_format):
    if prefix:
        prefix += "_"
    else:
        prefix = ""
    filename = Path("{}{}.{}".format(prefix, name, image_format))

    if directory:
        filename = directory / filename

    plt.savefig(filename, format=image_format, bbox_inches="tight", dpi=400)


def is_vasprun_file(filename):
    return "xml" in filename


def get_kpath(structure, mode="pymatgen", symprec=_symprec, kpt_list=None, labels=None):
    r"""Get a Kpath object

    If a manual list of kpoints is supplied using the `kpt_list`
    variable, the `mode` option will be ignored.

    Args:
        structure: The structure.
        mode: Method used for calculating the
            high-symmetry path. The options are:

            pymatgen
                Use the paths from pymatgen.

            seekpath
                Use the paths from SeeK-path.

        symprec: The tolerance for determining the crystal symmetry.
        kpt_list: List of k-points to use, formatted as a list of subpaths, each
            containing a list of fractional k-points. For example:

            ```
                [ [[0., 0., 0.], [0., 0., 0.5]], [[0.5, 0., 0.], [0.5, 0.5, 0.]] ]
            ```

            will return points along `0 0 0 -> 0 0 1/2 | 1/2 0 0 -> 1/2 1/2 0`
        labels: The k-point labels. These should be provided as a list of strings for
            each subpath of the overall path. For example::

            ```
                [ ['Gamma', 'Z'], ['X', 'M'] ]
            ```

            combined with the above example for `kpt_list` would indicate the path:
            `Gamma -> Z | X -> M`. If no labels are provided, letters from A -> Z will
            be used instead.

    Returns:
        A Kpath object.
    """
    from sumo.symmetry import CustomKpath, PymatgenKpath, SeekpathKpath

    if kpt_list:
        kpath = CustomKpath(structure, kpt_list, labels, symprec=symprec)
    elif mode == "seekpath":
        kpath = SeekpathKpath(structure, symprec=symprec)
    else:
        kpath = PymatgenKpath(structure, symprec=symprec)

    return kpath


def _get_dos_kpoints(structure, kpoints):
    from amset.electronic_structure.kpoints import get_kpoint_mesh

    if kpoints is None:
        return None

    splits = kpoints.split()
    if len(splits) == 1:
        return get_kpoint_mesh(structure, float(splits[0]))
    else:
        return list(map(int, splits))
