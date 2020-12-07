# reads out information and stores it correctly formatted

from operator import itemgetter
import os, csv

# global vars
alpha_level = .05
path = './'
path_o = './'
ending = '.txt'

# let the user input the name of the file
#fname = input("\n\nWrite the name of the exported txt file \n without folder and file ending:\n\n")
# select all files automatically from the input folder
all_files = [f for f in os.listdir(path) if f.endswith(ending)]

#fname = "test_analyse"

def get_reader_object(f):
    return open(path+f, 'r')

def get_inds_from_header(r):
    # df, F, p, eta**2
    relevant_inds = []
    # skip first 3 lines
    skipped = 0
    for line in r:
        skipped += 1
        if skipped <= 3:
            continue
        labels = line.split("|")
        for i, label in enumerate(labels):
            for query in ["df", "F", "Sig.", "Partielles"]:
                if label.startswith(query):
                    relevant_inds.append(i)
        break
    return relevant_inds

def separate_lines(r):
    # for every main/interaction effect, have a list containing:
    # name, df nom, df denom, F, p, eta**2
    # skip first 5 lines (TODO find out if already skipped)
    effects_obj = []
    skipped = 0
    for line in r:
        skipped += 1
        if skipped <= 1:
            continue
        if not line.startswith("|Fehler") and not line.startswith("| ") and not line.startswith("|-") and not line.startswith(" ") and not line.startswith("\n"):
            effects_obj.append([])
        if not line.startswith("|-"):
            effects_obj[-1].append(line)
    return effects_obj

def get_name(effect_lines):
    splitted = effect_lines[0].split("|")
    name = splitted[1].split("  ")[0] # remove spaces at the end
    return name

def get_dfs(effect_lines, inds):
    dfs = []
    # get ind of df
    ind_df = inds[0]
    # first df in first line
    splitted = effect_lines[0].split("|")
    df1 = int(splitted[ind_df + 1])
    dfs.append(df1)
    for line in effect_lines:
        if line.startswith("|Fehler"):
            splitted = line.split("|")
            df2 = int(splitted[ind_df + 1])
            dfs.append(df2)
    return dfs

def get_F(effect_lines, inds):
    # get ind of df
    ind_df = inds[1]
    # first df in first line
    replaced = effect_lines[0].replace(",", ".")
    splitted = replaced.split("|")
    F = float(splitted[ind_df + 1])
    return F

def get_p(effect_lines, inds):
    # get ind of df
    ind_df = inds[2]
    # first df in first line
    replaced = effect_lines[0].replace(",", ".")
    splitted = replaced.split("|")
    p = float(splitted[ind_df + 1])
    return p

def get_eta_squared(effect_lines, inds):
    # get ind of df
    ind_df = inds[3]
    # first df in first line
    replaced = effect_lines[0].replace(",", ".")
    splitted = replaced.split("|")
    eta_squared = float(splitted[ind_df + 1])
    return eta_squared

def append_values(effects, inds):
    all_effects = []
    for effect_lines in effects:
        all_effects.append([])
        all_effects[-1].append(get_name(effect_lines))
        all_effects[-1].append(get_dfs(effect_lines, inds))
        all_effects[-1].append(get_F(effect_lines, inds))
        all_effects[-1].append(get_p(effect_lines, inds))
        all_effects[-1].append(get_eta_squared(effect_lines, inds))
    return all_effects

def order_effects_to_p(effects_table):
    return sorted(effects_table, key=itemgetter(3))

def get_all_significant_effects(sorted_table):
    all_sigs = []
    for effect in sorted_table:
        if effect[3] <= alpha_level:
            all_sigs.append(effect)
    return all_sigs

def get_closest_to_sig_effect(sorted_table):
    for effect in sorted_table:
        if effect[3] > alpha_level:
            return effect

def get_writer_object(fname):
    return open(path_o+fname+".html", 'w')

def format_float(f, precision):
    # convert to string
    f_str = "{0:.{prec}f}".format(f, prec=precision)
    if f > 0:
        if f < 1:
            # remove zero
            return f_str[1:]
    elif f < 0:
        if f > -1:
            # remove zero but leave sign
            return f_str[0:1]+f_str[2:]
    return f_str

def format_factor_name(input_string):
    # create the dict from csv
    c = open(path+"replace_factor_names.csv", 'r')
    reader = csv.reader(c, delimiter=";")
    csv_list = list(reader)
    for item in csv_list:
        input_string = input_string.replace(item[0], item[1])
    input_string = input_string.replace("*", "&#215;")
    return input_string

def write_filename(w, fname):
    fname = fname.split(".")[0]
    html_text = """
    <b>{fname}:</b> <br><br>
    """
    formatted_html_text = html_text.format(fname=fname)
    w.write(formatted_html_text)

def write_formatted_effect(w, effect):
    # get the values --> convert to strings
    # TODO convert to strings 
    effect_name = format_factor_name(effect[0])
    df1 = str(effect[1][0])
    df2 = str(effect[1][1])
    F_val = format_float(effect[2], 2)
    p_val = format_float(effect[3], 3)
    eta_val = format_float(effect[4], 3)
    # prepare standard strings
    all_other = ""
    eta_part = "; &#951;<sub>p</sub><sup>2</sup> = " + eta_val
    p_sign = "="
    F_sign = "="
    # special cases
    if effect[3] < 0.001:
        p_sign = "&#60;"
        p_val = ".001"
    elif effect[3] > alpha_level:
        # non significant:
        p_sign = "&#8805;"
        F_sign = "&#8804;"
        all_other = "All other "
        eta_part = ""
    html_text = """
    <b>{effect_name}</b> <br>
    {all_other}F({df1}, {df2}) {F_sign} {F_val}; p {p_sign} {p_val}{eta_part} <br>
    """
    # include the variables
    formatted_html_text = html_text.format(effect_name=effect_name, all_other=all_other, df1=df1, df2=df2, F_sign=F_sign, F_val=F_val, p_sign=p_sign, p_val=p_val, eta_part=eta_part)
    w.write(formatted_html_text)

def close_writer(w):
    w.close()

# function calls
w = get_writer_object("all_ANOVAs_results")

for fname in all_files:
    print(fname)
    r = get_reader_object(fname)
    inds = get_inds_from_header(r)
    sep_lines = separate_lines(r)
    values_table = append_values(sep_lines, inds)
    sorted_table = order_effects_to_p(values_table)
    all_sigs = get_all_significant_effects(sorted_table)
    closest_sig = get_closest_to_sig_effect(sorted_table)

    # write the F tests
    write_filename(w, fname)
    for sig in all_sigs:
        write_formatted_effect(w, sig)
    w.write("<br>non-significant:<br>")
    write_formatted_effect(w, closest_sig)
    w.write("<br><br>")
close_writer(w)

# letting user know everything worked out
print("file saved under " + path_o + "all_ANOVAs_results" + ".html.")