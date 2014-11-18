"""
1. start cont1
2. start cont2 --ipc container:$cont1
3. start cont3 --ipc container:$cont2
4. start worker on cont3 (cont3 allocates the shm)
5. start workers on cont1 and cont2
6. wait until they finish
"""
import random

from run_ipc_mem import IpcBase


class cont1_c1cont2_w_c2cont3(IpcBase):

    def run_once(self):
        super(cont1_c1cont2_w_c2cont3, self).run_once()
        no_iter = self.config.get('no_iterations', 1024)
        key = self._find_hosts_free_ipc(random.randint(1, 65536))
        self.sub_stuff['shms'].append(key)
        str1 = 'a%s' % self._generate_string()
        str2 = 'b%s' % self._generate_string()
        str3 = 'c%s' % self._generate_string()
        # start containers
        c1_name = self._init_container_stdin('cont1', None)
        c2_name = self._init_container_stdin('cont2', "container:%s" % c1_name)
        self._init_container_stdin('cont3', "container:%s" % c2_name)
        # start worker on 3rd container
        args = "%s %s %s %s n" % (key, no_iter, str1, str2)
        self._exec_container_stdin(self.sub_stuff['cmds'][2], args)
        args = "%s %s %s %s n" % (key, no_iter, str2, str3)
        self._exec_container_stdin(self.sub_stuff['cmds'][1], args)
        args = "%s %s %s %s y" % (key, no_iter, str3, str1)
        self._exec_container_stdin(self.sub_stuff['cmds'][0], args)

    def postprocess(self):
        super(cont1_c1cont2_w_c2cont3, self).postprocess()
        timeout = self.parent_subtest.adjust_timeout(120)
        self.sub_stuff['cmds'][0].wait_check(timeout)
        timeout = self.parent_subtest.adjust_timeout(15)
        self.sub_stuff['cmds'][1].wait_check(timeout)
        timeout = self.parent_subtest.adjust_timeout(15)
        self.sub_stuff['cmds'][2].wait_check(timeout)
        self.sub_stuff['cmds'] = []
        self.sub_stuff['shms'] = []
