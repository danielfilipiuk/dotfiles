from UM.Math.Vector import Vector
from UM.Logger import Logger

import numpy as np

def getFacePlaneVectors(mesh_data, face_id):
    point, normal = mesh_data.getFacePlane(face_id)
    return Vector(data=point), Vector(data=normal).normalized()

def getFaceArea(mesh_data, face_id):
    a, b, c = mesh_data.getFaceNodes(face_id)
    ab = Vector(data=(b - a))
    ac = Vector(data=(c - a))
    area = 0.5 * ab.cross(ac).length()
    return area

def calculateCenterOfMassAndArea(mesh_data, face_list):
    weighted_sum = Vector()
    total_area = 0
    for face in face_list:
        c, _ = getFacePlaneVectors(mesh_data, face)
        area = getFaceArea(mesh_data, face)
        weighted_sum += c * area
        total_area += area

    center = weighted_sum / total_area if total_area != 0 else Vector()
    return center, total_area

def findFlatSurface(mesh_data, face_id, all_faces, ids, threshold=3e-4):
    stack = [face_id]
    while stack:
        current_face_id = stack.pop(0)
        ids.append(current_face_id)
        _, face_normal = getFacePlaneVectors(mesh_data, current_face_id)
        for neighbor in all_faces[current_face_id]:
            neighbor_id = neighbor.face_id
            if neighbor_id in ids or neighbor_id in stack:
                continue
            _, neighbor_normal = getFacePlaneVectors(mesh_data, neighbor_id)
            if (1 - np.abs(face_normal.dot(neighbor_normal))) < threshold:
                stack.append(neighbor_id)

def findConvexSurface(mesh_data, face_id, all_faces, ids):
    return _findCurvedSurface(mesh_data, face_id, all_faces, ids, True)

def findConcaveSurface(mesh_data, face_id, all_faces, ids):
    return _findCurvedSurface(mesh_data, face_id, all_faces, ids, False)

# TODO: this one should be improved, but again, not the priority right now
def _findCurvedSurface(mesh_data, face_id, all_faces, ids, is_convex_surface,
                       circle_threshold_neighbor_angle = np.pi * 20 / 180):
    face_center, face_normal = getFacePlaneVectors(mesh_data, face_id)

    # find plane Ax+By+Cz+D=0 of the face
    base_ABC = face_normal
    base_D = -face_center.dot(base_ABC)

    potential_partial_cylinder_ids = [{'ids': [face_id], 'axis': None}]

    for neighbor in all_faces[face_id]:
        potential_cylinder_ids = [face_id, neighbor.face_id]
        neighbor_center, neighbor_normal = getFacePlaneVectors(mesh_data, neighbor.face_id)
        # TODO: this can fail for neighbors that are nearly coplanar, consider improvement
        is_convex = base_ABC.dot(neighbor_center) + base_D >= 0
        if is_convex != is_convex_surface:
            continue

        dot_product = base_ABC.dot(neighbor_normal)
        angle_magnitude_check = np.arccos(np.clip(dot_product, -1.0, 1.0))
        if angle_magnitude_check > circle_threshold_neighbor_angle:
            continue
        base_ABC = neighbor_normal
        base_D = -neighbor_center.dot(base_ABC)
        edge_center = neighbor.edge_center
        potential_cylinder_axis_vector = face_normal.cross(neighbor_normal).normalized()

        # # TODO: for now, only whole cylinders can be detected; this should be improved
        if _detectCylinder(mesh_data, face_normal, face_id, edge_center, neighbor.face_id, is_convex_surface,
                           potential_cylinder_axis_vector, base_ABC, base_D, all_faces, True,
                           potential_cylinder_ids):
            Logger.log('d', 'cylinder found')
            ids.extend(potential_cylinder_ids)
            # distances = []
            # axis = Vector(-1, 0, 0)
            # plane_ABC = axis
            # for id in ids:
            #     c, n = getFacePlaneVectors(self._highlights_manager.getMeshData(), id)
            #     # c = calculateCenterOfMass(self._highlights_manager.getMeshData(), [id])
            #     if id == ids[0]:
            #         base_point = c
            #         base_n = n
            #         plane_D = -c.dot(plane_ABC)
            #         continue
            #     d = plane_ABC.dot(c) + plane_D
            #     c_p = c - d * axis
            #     dot_product = base_n.dot(n)
            #     dist = (base_point - c_p).length()
            #     angle = np.arccos(np.clip(dot_product, -1.0, 1.0))
            #     r = np.sqrt(-(dist * dist) / (2 * (np.cos(angle) - 1)))
            #     # c = calculateCenterOfMass(self._highlights_manager.getMeshData(), [id])
            #     # c_p = (c.dot(potential_cylinder_axis_vector) / potential_cylinder_axis_vector.dot(potential_cylinder_axis_vector)) * potential_cylinder_axis_vector
            #     # r = (c - c_p).length()
            #     distances.append(r)
            # print(distances)
            return True, potential_cylinder_axis_vector
        else:
            print('potential partial cylinder detected')
            potential_cylinder_ids = potential_cylinder_ids[::-1]
            _detectCylinder(mesh_data, face_normal, face_id, edge_center, face_id, is_convex_surface,
                            potential_cylinder_axis_vector, base_ABC, base_D, all_faces, True,
                            potential_cylinder_ids, False)
            potential_partial_cylinder_ids.append({'ids': potential_cylinder_ids,
                                                   'axis': potential_cylinder_axis_vector})

    best_potential_cylinder_ids = [face_id]
    best_potential_cylinder_score = np.inf
    for item in potential_partial_cylinder_ids:
        print(item['ids'])
        axis = item['axis']
        current_ids = item['ids']
        if axis is None or axis == Vector():
            print(f'Invalid axis: {axis}')
            continue
        plane_ABC = axis
        distances = []
        base_item = current_ids.pop(len(current_ids) // 2)
        kept_items = [base_item]
        base_point, base_n = getFacePlaneVectors(mesh_data, base_item)
        plane_D = -base_point.dot(plane_ABC)
        for id in current_ids:
            c, n = getFacePlaneVectors(mesh_data, id)
            # if id == item['ids'][0]:
            #     base_point = c
            #     base_n = n
            #     plane_D = -c.dot(base_ABC)
            #     continue
            d = plane_ABC.dot(c) + plane_D
            c_p = c - d * axis
            dot_product = base_n.dot(n)
            dist = (base_point - c_p).length()
            angle = np.arccos(np.clip(dot_product, -1.0, 1.0))
            if angle < 0.1:
                print(f'Adding {id} to kept items')
                kept_items.append(id)
            else:
                r = np.sqrt(-(dist * dist) / (2 * (np.cos(angle) - 1)))
                if not np.isnan(r):
                    distances.append(r)
                else:
                    print('R is nan; how to approach this?')
                    # TODO: fix this
                    distances.append(0)
        current_ids = [i for i in current_ids if i not in kept_items]
        cv = np.std(distances) / np.median(distances)
        # print(f'cv: {cv}')
        # current_ids = np.array(current_ids)
        # scaling_factor = 1.4826
        # threshold = 10.0
        # distances = np.array(distances)
        # median = np.median(distances)
        # abs_deviation = np.abs(distances - median)
        # mad = np.median(abs_deviation)
        # modified_z_score = abs_deviation / (scaling_factor * mad)
        # current_ids = current_ids[modified_z_score <= threshold]
        # current_ids = list(current_ids)
        current_ids.extend(kept_items)
        if np.isnan(best_potential_cylinder_score) or cv < best_potential_cylinder_score:
            best_potential_cylinder_score = cv
            best_potential_cylinder_ids = current_ids

    # nothing found
    ids.extend(best_potential_cylinder_ids)
    # ids.extend(potential_cylinder_ids)
    # ids.append(face_id)
    return False, None

# TODO: this one should be improved, but again, not the priority right now
def _detectCylinder(mesh_data, origin_normal, origin_id, previous_edge_center, previous_id, is_convex_surface,
                    potential_cylinder_axis, base_ABC, base_D, all_faces, first_run, ids, whole=True,
                    circle_threshold_neighbor_angle = np.pi * 20 / 180, flat_threshold = 1e-2):
    viable_neighbors = {}
    for neighbor in all_faces[previous_id]:
        if neighbor.face_id == origin_id:
            if first_run or not whole:
                continue
            else:
                return True

        if neighbor.face_id in ids:
            continue

        neighbor_center, neighbor_normal = getFacePlaneVectors(mesh_data, neighbor.face_id)
        dot_product = base_ABC.dot(neighbor_normal)
        angle_magnitude_check = np.arccos(np.clip(dot_product, -1.0, 1.0))
        is_convex = base_ABC.dot(neighbor_center) + base_D >= 0
        if (1 - np.abs(dot_product)) > flat_threshold:
            if is_convex != is_convex_surface:
                continue

        pass_condition = angle_magnitude_check < circle_threshold_neighbor_angle
        if (1 - np.abs(origin_normal.dot(neighbor_normal))) > flat_threshold:
            perpendicular_vec = origin_normal.cross(neighbor_normal).normalized()
            pass_condition = pass_condition and 1 - np.abs(potential_cylinder_axis.dot(perpendicular_vec)) < 2e-2

        if pass_condition:
            viable_neighbors[neighbor.face_id] = {'edge_center': neighbor.edge_center, 'normal': neighbor_normal,
                                                  'center': neighbor_center, 'id': neighbor.face_id}

    smallest_direction_change = 1
    smallest_direction_neighbor = None
    for k, v in viable_neighbors.items():
        direction = (previous_edge_center - v['edge_center']).normalized()
        direction_change = (1 - np.abs(direction.cross(v['normal']).dot(potential_cylinder_axis)))
        if direction_change < smallest_direction_change:
            smallest_direction_change = direction_change
            smallest_direction_neighbor = v

    if smallest_direction_neighbor is None:
        return False
    else:
        face_id = smallest_direction_neighbor['id']
        ids.append(face_id)

        base_ABC = smallest_direction_neighbor['normal']
        base_D = -smallest_direction_neighbor['center'].dot(base_ABC)
        result = _detectCylinder(mesh_data, origin_normal, origin_id, smallest_direction_neighbor['edge_center'],
                                 face_id, is_convex_surface, potential_cylinder_axis, base_ABC, base_D,
                                 all_faces, False, ids, whole)
        return result

def cylinderResiduals(params, points):
    cx, cy, cz, nx, ny, nz, r = params
    vecs = points - np.array([cx, cy, cz])
    projected_lengths = np.dot(vecs, np.array([nx, ny, nz]))
    projected_points = vecs - np.outer(projected_lengths, np.array([nx, ny, nz]))
    distances = np.linalg.norm(projected_points, axis=1)
    return distances - r