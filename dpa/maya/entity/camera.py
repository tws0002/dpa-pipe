
import os.path
import re

from dpa.app.entity import EntityRegistry, EntityError
from dpa.maya.entity.base import SetBasedWorkfileEntity

# -----------------------------------------------------------------------------
class CameraEntity(SetBasedWorkfileEntity):

    category = "camera"

    # -------------------------------------------------------------------------
    @classmethod
    def import_product_representation(cls, session, representation, *args,
        **kwargs):

        if representation.type == 'ma':
            super(CameraEntity, cls).import_product_representation(
                session, representation, *args, **kwargs)    
        else:
            if representation.type != 'fbx':
                raise EntityError(
                    "Unknown type for {cat} import: {typ}".format(
                        cls=cls.category, typ=representation.type))

            cls._fbx_import(session, representation, *args, **kwargs)

    # -------------------------------------------------------------------------
    def export(self, product_desc=None, version_note=None, fbx_export=False,
        fbx_options=None, ma_export=False, ma_options=None):
    
        product_reprs = []

        if fbx_export:
            product_reprs.extend(
                self._fbx_export(fbx_options, product_desc, version_note)
            )

        if ma_export:
            product_reprs.extend(
                self._ma_export(ma_options, product_desc, version_note)
            )

        return product_reprs

    # -------------------------------------------------------------------------
    def _fbx_export(self, options, product_desc, version_note):

        self.session.require_plugin('fbxmaya')

        file_type = 'fbx'

        product_repr = self._create_product(product_desc, version_note,
            file_type)
        product_repr_dir = product_repr.directory

        export_objs = self.get_export_objects()

        export_path = os.path.join(product_repr_dir, self.display_name)

        with self.session.selected(export_objs):
            self.session.mel.eval(
                'FBXExport -f "{path}" -s'.format(path=export_path))

        product_repr.area.set_permissions(0660)

        return [product_repr]
    
    # -------------------------------------------------------------------------
    def _ma_export(self, options, product_desc, version_note):

        file_type = 'ma'

        product_repr = self._create_product(product_desc, version_note,
            file_type)
        product_repr_dir = product_repr.directory
        product_repr_file = os.path.join(
            product_repr_dir, self.display_name + "." + file_type)

        export_objs = self.get_export_objects()

        with self.session.selected(export_objs):
            self.session.cmds.file(
                product_repr_file, 
                type='mayaAscii', 
                exportSelected=True,
                force=True, 
                preserveReferences=False,
            )

        product_repr.area.set_permissions(0660)

        return [product_repr]

# -----------------------------------------------------------------------------
EntityRegistry().register('maya', CameraEntity)

