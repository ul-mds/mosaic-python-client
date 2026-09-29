-- version from 2026-06-17 RS

-- Schema verwenden
\c gras;

-- domain
CALL createDomain('ths', 'parent domain');

-- project
CALL createProject('gpas', 'gPAS');

-- group_
CALL createGroup('gpas', 'gPAS-users', 'this group is for users with basic right');
CALL createGroup('gpas', 'gPAS-admins', 'this group is for users with extended right');

-- role
CALL createRole('gpas', 'role.gpas.user', 'gPAS userspace');
CALL createRole('gpas', 'role.gpas.admin', 'gPAS adminspace');

-- group_role_mapping
CALL createGroupRoleMapping('gpas', 'gPAS-users', 'role.gpas.user');
CALL createGroupRoleMapping('gpas', 'gPAS-admins', 'role.gpas.user');
CALL createGroupRoleMapping('gpas', 'gPAS-admins', 'role.gpas.admin');

-- default user
CALL createUser('admin', 'ttp-tools', 'user for admin privileges');
CALL createUser('user', 'ttp-tools', 'user for standard privileges');

-- grant privileges for project
CALL grantAdminRights('ths', 'gpas', 'admin');
CALL grantStandardRights('ths', 'gpas', 'user');
