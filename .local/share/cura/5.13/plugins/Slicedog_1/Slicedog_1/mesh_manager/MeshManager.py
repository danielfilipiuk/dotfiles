from UM.Math.Vector import Vector

from dataclasses import dataclass
from typing import Optional, Callable

@dataclass
class NeighborObject:
    face_id: int
    edge_center: Vector

    def __init__(self, face_id: int, edge_center: Vector):
        self.face_id = face_id
        self.edge_center = edge_center

class MeshManager:
    def __init__(self, progress_callback: Optional[Callable[[str], None]] = None):
        self._mesh_data = None
        self._cached_meshes = {}
        self._progress_callback = progress_callback

    def cacheMeshWithAdjacency(self, name, mesh):
        self._cached_meshes[name] = mesh

    def getCachedMeshWithAdjacency(self, name):
        return self._cached_meshes.get(name, None)

    def setProgressCallback(self, callback: Optional[Callable[[str], None]] = None):
        self._progress_callback = callback

    def setMeshData(self, mesh_data):
        self._mesh_data = mesh_data

    def getMeshData(self):
        return self._mesh_data

    def buildEdgeConnectivity(self):
        # TODO: could this be moved somewhere else so it does not need to wait until you click on some face?
        mesh_vertices = self._mesh_data.getVertices()

        N = int(self._mesh_data.getVertexCount() / 3)
        connectivity = {}

        for i in range(0, N):
            t = mesh_vertices[[i * 3, i * 3 + 1, i * 3 + 2]]
            for e in range(3):
                v1 = t[e]
                v2 = t[(e + 1) % 3]
                he = _edgeHash(v1, v2)
                center = Vector(data=(v1 + v2) / 2)
                connectivity.setdefault(he, {})
                connectivity[he].setdefault('ids', [])
                connectivity[he]['ids'].append(i)
                connectivity[he]['center'] = center
            if self._progress_callback and i % 10000 == 0:
                self._progress_callback(f'Part 1 of 2: {(100 * i) // N}% finished')

        return connectivity

    def buildFaceAdjacency(self, connectivity):
        all_faces = {}
        for i, edge_pair in enumerate(connectivity.values()):
            ids = edge_pair['ids']
            center = edge_pair['center']
            f0 = ids[0]
            f1 = ids[1]
            all_faces.setdefault(f0, [])
            all_faces.setdefault(f1, [])
            all_faces[f0].append(NeighborObject(face_id=f1, edge_center=center))
            all_faces[f1].append(NeighborObject(face_id=f0, edge_center=center))

            # this loop is too quick and feedback does not show correctly, so don't send it that often
            if self._progress_callback and i % 100000 == 0:
                self._progress_callback(f'Part 2 of 2: {(100 * i) // len(connectivity)}% finished')

        return all_faces

        # TODO: consider improving the speed of building adjacency - code below should be faster and correct. Not a
        #  priority right now
        # start = time.time()
        # mesh_faces = self._highlights_manager.getMeshData().getIndices()
        # if mesh_faces is None:
        #     mesh_faces = np.arange(len(mesh_vertices)).reshape(len(mesh_vertices) // 3, 3)
        # mesh = trimesh.Trimesh(vertices=mesh_vertices, faces=mesh_faces, process=True)
        #
        # # Extract adjacency information
        # adjacency = mesh.face_adjacency
        # edge_indices = mesh.face_adjacency_edges
        #
        # # Compute edge centers correctly, one per edge pair
        # edge_centers = mesh.vertices[edge_indices].mean(axis=1)
        #
        # # Construct the neighbor data array
        # num_pairs = len(adjacency)
        # neighbor_data = np.zeros(num_pairs * 2, dtype=[
        #     ('face_id', np.int32),
        #     ('neighbor_id', np.int32),
        #     ('center_x', np.float32),
        #     ('center_y', np.float32),
        #     ('center_z', np.float32)
        # ])
        #
        # # Populate the array
        # # First half: f1 -> f2
        # neighbor_data['face_id'][:num_pairs] = adjacency[:, 0]
        # neighbor_data['neighbor_id'][:num_pairs] = adjacency[:, 1]
        # neighbor_data['center_x'][:num_pairs] = edge_centers[:, 0]
        # neighbor_data['center_y'][:num_pairs] = edge_centers[:, 1]
        # neighbor_data['center_z'][:num_pairs] = edge_centers[:, 2]
        #
        # # Second half: f2 -> f1 (reversed order)
        # neighbor_data['face_id'][num_pairs:] = adjacency[:, 1]
        # neighbor_data['neighbor_id'][num_pairs:] = adjacency[:, 0]
        # neighbor_data['center_x'][num_pairs:] = edge_centers[:, 0]
        # neighbor_data['center_y'][num_pairs:] = edge_centers[:, 1]
        # neighbor_data['center_z'][num_pairs:] = edge_centers[:, 2]
        #
        # end = time.time()
        # print(f'Neighbor data time elapsed: {end-start} s')
        #
        # start = time.time()
        # face_ids = neighbor_data['face_id']
        # neighbor_ids = neighbor_data['neighbor_id']
        # centers = neighbor_data[['center_x', 'center_y', 'center_z']]
        #
        # # Use numpy unique with return_inverse to avoid multiple scans
        # unique_faces, inverse_indices = np.unique(face_ids, return_inverse=True)
        #
        # # Initialize defaultdict with fixed-size lists
        # lookup_dict = {face_id: [] for face_id in unique_faces}
        #
        # # Populate the dictionary in a single pass
        # for idx, fid in enumerate(face_ids):
        #     # lookup_dict[face_id].append((neighbor_ids[idx], tuple(centers[idx])))
        #     lookup_dict[fid].append(
        #         NeighborObject(face_id=neighbor_ids[idx], edge_center=Vector(*centers[idx])))
        #
        # all_faces = lookup_dict
        # end = time.time()
        # print(f'Lookup dict time elapsed: {end-start} s')
        #
        # for k, v in lookup_dict.items():
        #     v2 = all_faces[k]
        #
        #     for n1 in v:
        #         any_equal = False
        #         for n2 in v2:
        #             if n1 == n2:
        #                 any_equal = True
        #
        #         if not any_equal:
        #             print('Something not right')
        #
        # for nd in neighbor_data:
        #     fid = nd['face_id']
        #     nid = nd['neighbor_id']
        #     center = Vector(nd['center_x'], nd['center_y'], nd['center_z'])
        #     same_neighbor = False
        #     for neighbor in all_faces[fid]:
        #         if nid == neighbor.face_id:
        #             same_neighbor = True
        #             if center != neighbor.edge_center:
        #                 print('Edge centers not same!')
        #     if not same_neighbor:
        #         print('Neighbor not same!')


def _edgeHash(v1, v2):
    tol = 1e-5
    h1 = hash((int(v1[0] / tol), int(v1[1] / tol), int(v1[2] / tol)))
    h2 = hash((int(v2[0] / tol), int(v2[1] / tol), int(v2[2] / tol)))
    forward = hash((h1, h2))
    backward = hash((h2, h1))
    return forward ^ backward