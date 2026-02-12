using Pkg; Pkg.activate("."); Pkg.instantiate()
using HiRepParsing
using HDF5
using DelimitedFiles
Pkg.add("ArgParse")
using ArgParse
using YAML

function parse_commandline()
    s = ArgParseSettings()
    @add_arg_table s begin
        "--h5file"
            help = "Path to the output HDF5 file."
            required = true
        "--ensemble"
            help = "Ensemble name to process."
            required = true
        "--config_yaml"
            help = "Path to the YAML configuration file."
            required = true
    end
    return parse_args(s)
end

function main(h5file;ensemble,rep,disc,nhits,file,setup=true,filter_channels=false,channels=nothing)
    #isfile(h5file) && rm(h5file)
    if disc == "DISC"
        smearing_regex = r"DISCON_SEMWALL smear_N[0-9]+ SINGLET"
        h5group = joinpath(ensemble,rep,disc)
        writehdf5_spectrum_disconnected_with_regexp(file,h5file,smearing_regex,nhits;mixed_rep=false,h5group=h5group,setup,filter_channels,channels,sort=true,deduplicate=true)
    else
        smearing_regex = r"source_N[0-9]+_sink_N[0-9]+ TRIPLET"
        h5group = joinpath(ensemble,rep,disc)
        writehdf5_spectrum_with_regexp(file,h5file,smearing_regex;mixed_rep=false,h5group=h5group,setup,filter_channels,channels,sort=true,deduplicate=true)
    end
end

args = parse_commandline()
output_dir = args["h5file"] 
ensemble = args["ensemble"]
config_yaml = args["config_yaml"]
config = YAML.load_file(config_yaml)

filename = joinpath(output_dir, ensemble * "_spectrum.hdf5")

for rep in keys(config["ensembles"][ensemble]["rep"])
    disc_input_file = config["ensembles"][ensemble]["rep"][rep]["disc_input_file"]
    conn_input_file = config["ensembles"][ensemble]["rep"][rep]["conn_input_file"]
    ndisc_hits = config["ensembles"][ensemble]["rep"][rep]["disc_nhits"]
    nconn_hits = 1
    conn_str = "CONN"
    disc_str = "DISC"

    # Write connected contributions
    main(filename; ensemble, rep, disc=conn_str, nhits=nconn_hits, file=conn_input_file, filter_channels=false, channels=nothing)
    
    # Write disconnected contributions
    main(filename; ensemble, rep, disc=disc_str, nhits=ndisc_hits, file=disc_input_file, filter_channels=false, channels=nothing)
end
