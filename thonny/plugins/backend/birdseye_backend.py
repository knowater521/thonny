import os

from thonny.backend import Executor, get_backend, prepare_hooks, return_execution_result


def _cmd_Birdseye(cmd):
    backend = get_backend()
    backend.switch_env_to_script_mode(cmd)
    return backend._execute_file(cmd, BirdsEyeRunner)


class BirdsEyeRunner(Executor):
    @return_execution_result
    @prepare_hooks
    def execute_source(self, source, filename, mode, ast_postprocessors):
        import webbrowser

        assert mode == "exec"
        # ignore ast_postprocessors, because birdseye requires source

        if isinstance(source, bytes):
            source = source.decode("utf-8")

        import __main__  # @UnresolvedImport

        global_vars = __main__.__dict__

        # Following is a trick, which allows importing birdseye in the backends,
        # which doesn't have it installed (provided it is installed for frontend Python)
        self._backend.load_modules_with_frontend_path(["birdseye.bird"])
        from birdseye.bird import eye

        eye.exec_string(source, filename, globs=global_vars, locs=global_vars, deep=True)
        port = os.environ.get("BIRDSEYE_PORT", "7777")
        webbrowser.open_new_tab("http://localhost:%s/ipython_call/" % port + eye._last_call_id)


def load_plugin():
    get_backend().add_command("Birdseye", _cmd_Birdseye)
