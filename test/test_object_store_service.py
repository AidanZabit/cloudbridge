from io import BytesIO
import uuid

from test.helpers import ProviderTestBase
import test.helpers as helpers


class CloudObjectStoreServiceTestCase(ProviderTestBase):

    def __init__(self, methodName, provider):
        super(CloudObjectStoreServiceTestCase, self).__init__(
            methodName=methodName, provider=provider)

    def test_crud_container(self):
        """
        Create a new container, check whether the expected values are set,
        and delete it
        """
        name = "cbtestcreatecontainer-{0}".format(uuid.uuid4())
        test_container = self.provider.object_store.create(name)
        with helpers.cleanup_action(lambda: test_container.delete()):
            self.assertTrue(
                test_container.id in repr(test_container),
                "repr(obj) should contain the object id so that the object"
                " can be reconstructed, but does not. eval(repr(obj)) == obj")

            containers = self.provider.object_store.list()

            found_containers = [c for c in containers if c.name == name]
            self.assertTrue(
                len(found_containers) == 1,
                "List containers does not return the expected container %s" %
                name)

            # check iteration
            found_containers = [c for c in self.provider.object_store
                                if c.name == name]
            self.assertTrue(
                len(found_containers) == 1,
                "Iter containers does not return the expected container %s" %
                name)

            get_container = self.provider.object_store.get(
                test_container.id)
            self.assertTrue(
                found_containers[0] ==
                get_container == test_container,
                "Objects returned by list: {0} and get: {1} are not as "
                " expected: {2}" .format(found_containers[0].id,
                                         get_container.id,
                                         test_container.name))

        containers = self.provider.object_store.list()
        found_containers = [c for c in containers if c.name == name]
        self.assertTrue(
            len(found_containers) == 0,
            "Container %s should have been deleted but still exists." %
            name)

    def test_crud_container_objects(self):
        """
        Create a new container, upload some contents into the container, and
        check whether list properly detects the new content.
        Delete everything afterwards.
        """
        name = "cbtestcontainerobjs-{0}".format(uuid.uuid4())
        test_container = self.provider.object_store.create(name)

        # ensure that the container is empty
        objects = test_container.list()
        self.assertEqual([], objects)

        with helpers.cleanup_action(lambda: test_container.delete()):
            obj_name = "hello_world.txt"
            obj = test_container.create_object(obj_name)

            self.assertTrue(
                obj.id in repr(obj),
                "repr(obj) should contain the object id so that the object"
                " can be reconstructed, but does not. eval(repr(obj)) == obj")

            with helpers.cleanup_action(lambda: obj.delete()):
                # TODO: This is wrong. We shouldn't have to have a separate
                # call to upload some content before being able to delete
                # the content. Maybe the create_object method should accept
                # the file content as a parameter.
                obj.upload("dummy content")
                objs = test_container.list()

                # check iteration
                iter_objs = list(test_container)
                self.assertListEqual(iter_objs, objs)

                found_objs = [o for o in objs if o.name == obj_name]
                self.assertTrue(
                    len(found_objs) == 1,
                    "List container objects does not return the expected"
                    " object %s" % obj_name)

                self.assertTrue(
                    found_objs[0] == obj,
                    "Objects returned by list: {0} are not as "
                    " expected: {1}" .format(found_objs[0].id,
                                             obj.id))

            objs = test_container.list()
            found_objs = [o for o in objs if o.name == obj_name]
            self.assertTrue(
                len(found_objs) == 0,
                "Object %s should have been deleted but still exists." %
                obj_name)

    def test_upload_download_container_content(self):

        name = "cbtestcontainerobjs-{0}".format(uuid.uuid4())
        test_container = self.provider.object_store.create(name)

        with helpers.cleanup_action(lambda: test_container.delete()):
            obj_name = "hello_upload_download.txt"
            obj = test_container.create_object(obj_name)

            with helpers.cleanup_action(lambda: obj.delete()):
                content = b"Hello World. Here's some content"
                # TODO: Upload and download methods accept different parameter
                # types. Need to make this consistent - possibly provider
                # multiple methods like upload_from_file, from_stream etc.
                obj.upload(content)
                target_stream = BytesIO()
                obj.download(target_stream)
                self.assertEqual(target_stream.getvalue(), content)