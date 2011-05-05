from __future__ import with_statement
import Xenadu, ConfigParser, os, string, logging
#from distutils import dir_util
#from Xenadu.Task.Ssh import ssh

def render_path(outpath, pathname, h):
    for filename in os.listdir(pathname):
        fullfile = os.path.join(pathname, filename)
        logging.getLogger("Xenadu").debug("start %s" % fullfile)

        p = pathname.split('/')[1:]
        if len(p) > 0:
            p = os.path.join(*p)
        else:
            p = "."

        if os.path.isdir(fullfile):
            try:
                p2 = os.path.join(outpath, p, filename)
                logging.getLogger("Xenadu").debug("make path %s" % p2)
                os.mkdir(p2)
            except OSError as (num, msg):
                if num == 17:
                    pass
            render_path(outpath, fullfile, h)
        else:
            with open(fullfile, 'r') as f:
                raw = f.read()
            t = string.Template(raw)
            rendered = t.safe_substitute(h)
            outfile = os.path.join(outpath, p, filename)
            logging.getLogger("Xenadu").debug("writing %s" % outfile)
            with open(outfile, "w") as f:
                f.write(rendered)

def apply_template(*args):
    [config_file] = args
    cfg = None
    if config_file:
        cfg = ConfigParser.ConfigParser()
        cfg.read(config_file)
        try:
            h = dict(cfg.items('xenadu'))
        except ConfigParser.NoSectionError:
            logging.getLogger("Xenadu").error("cannot read: %s" % config_file)
            return
    else:
        logging.getLogger("Xenadu").error("usage: --template [filename]")

    try:
        os.mkdir("tmpl_files")
    except OSError as (num, msg):
        if num == 17:
            pass

    # copy the whole static tree over to tmpl_files.
    #dir_util.copy_tree("tmpl_static", "tmpl_files")

    # iterate through all files in tmpl.
    logging.getLogger("Xenadu").debug("values: %s" % h)
    render_path("tmpl_files", "tmpl", h)

def register():
    Xenadu.Env["Registry"].register_task(name="template", args=1, help="apply template", function=apply_template)
