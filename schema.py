# Copyright Notice:
# Copyright 2016-2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/LICENSE.md

###################################################################################################
# File: schema.py
# Description:  This module contains classes and functions used to trace out the Redfish schemas
#               according to OData v4.0 Schema representation and to seaarch within them for testing
#               and conformance purpose. Some classes in this file represent strucutures defined in
#               OData CSDL and related member helper functions. While class SchemaModel contains
#               functions to open the schema files and serialize them into relevant structures
#               defined in this module and collect them as a list for the client tool. For more info
#               on any Schema Element defined here, refer to Redfish Specification and OData Version
#               4.0 Part 3: CSDL: http://docs.oasis-open.org/odata/odata/v4.0/errata02/os/complete/
#
# Verified/operational Python revisions (Windows OS) :
#       2.7.10
#       3.4.3
#
# Initial code released : 01/2016
#   Steve Krig      ~ Intel
#   Fatima Saleem   ~ Intel
#   Priyanka Kumari ~ Texas Tech University
###################################################################################################

import io
import os
import xml.etree.ElementTree as ET
import copy
from collections import OrderedDict, OrderedDict


## Element tag mapping to its csdl namespace. 
## Used to prepend to an element tag to properly annotate them making it easier to search within the schema element tree
csdlNamespace = dict.fromkeys(['Edmx', 'DataServices', 'Reference', 'Include', 'reference'], '{http://docs.oasis-open.org/odata/ns/edmx}')
csdlNamespace.update(dict.fromkeys(['Schema', 'Property', 'NavigationProperty', 'EntityType' , 'ComplexType', 'EnumType' , 'Member' , 'Action' , 'Term' , 'Annotation', 'Parameter'], '{http://docs.oasis-open.org/odata/ns/edm}'))

###################################################################################################
# Class Edmx:
#   This class represents the edmx Element: Edmx. Edmx is the root element of every OData schema 
#   document, it contains a single DataServices element and zero or more Reference elements 
###################################################################################################
class Edmx:
    def __init__(self, schema_filename, edmx, version=None):
        self.SchemaUri = schema_filename # custom field
        self.edmx = edmx
        self.Version = version
        self.References = []
        self.DataServices = None 

    ###############################################################################################
    # Name: add_reference(edmx)
    #   add (list append) a Reference element to Edmx element
    ###############################################################################################
    def add_reference(self, reference):
        self.References.append(reference)

    ###############################################################################################
    # Name: add_dataservice(edmx)
    #   add a dataservice element to Edmx element
    ###############################################################################################
    def add_dataservice(self, dataservices):
        self.DataServices = dataservices

###################################################################################################
# Class Reference:
#   This class represents the edmx Element: Reference. It contains atleast one Include element and 
#   Uri which references an external CSDL document
###################################################################################################
class Reference:
    def __init__(self, uri):
        self.Uri = uri
        self.Includes = []  

    ###############################################################################################
    # Name: add_include(reference)
    #   add (list append) an Include element to Reference element
    ###############################################################################################
    def add_include(self, include):

        self.Includes.append(include)

###################################################################################################
# Class Include:
#   This class represents the edmx Element: Include. Include is within Reference element. It 
#   specifies which parts of the referenced CSDL documents are availoable for use.
###################################################################################################
class Include:
    def __init__(self, namespace, alias=None):
        self.Namespace = namespace
        self.Alias = alias

###################################################################################################
# Class DataServices: 
#   This class represents the edmx Element: DataServices. It is a schema container containing one 
#   or more Schema elements. It contains a custom field to store the Schema document path
###################################################################################################
class DataServices:
    def __init__(self, schema_uri):
        self.SchemaUri = schema_uri # custom field
        self.Schemas = []
    
    ###############################################################################################
    # Name: add_schema(dataservice)
    #   add (list append) a schema element to DataServices element 
    ###############################################################################################
    def add_schema(self, schema):
        self.Schemas.append(schema)

    ###############################################################################################
    # Name: get_all_entitytypes
    #   Returns entitytpes list within the Schemas in this DataService element
    ###############################################################################################
    def get_all_entitytypes(self):
        for ns in self.Schemas:
            return ns.EntityTypes

    ###############################################################################################
    # Name: find_ns_in_dataservices(namespace)
    #   Takes in the value of the Namespace property found in Schema element. Searches all the 
    #   Schema elements within the Dataservice element to match the Namespace property's value to 
    #   the value passed to this function. 
    #   Returns:
    #       The schema instance for that Namespace  
    ###############################################################################################
    def find_ns_in_dataservices(self, namespace):
        for ns in self.Schemas:
            if ns.Namespace == namespace:
                return ns
        return None

###################################################################################################
# Class Schema:
#   This class represents the edm Element: Schema. Schema is within edmx:DataServices. It contains
#   one or more following elements: Action, Annotation, ComplexType, EntityContainer, EntityType,
#   EnumType. It contains a custom field to store the Schema document path
###################################################################################################
class Schema:
    def __init__(self, name, schema_uri):
        self.Namespace = name
        self.SchemaUri = schema_uri # custom field
        self.EntityTypes = []
        self.ComplexTypes = []
        self.EnumTypes = []
        self.Actions = []

    ###############################################################################################
    # Name: add_entitytype(entitytype)
    #   add (list append) an EntityType element to Schema element 
    ###############################################################################################
    def add_entitytype(self, entitytype):
        self.EntityTypes.append(entitytype)

    ###############################################################################################
    # Name: add_complextype(complextype)
    #   add (list append) a ComplexType element to Schema element 
    ###############################################################################################
    def add_complextype(self, complextype):
        self.ComplexTypes.append(complextype)

    ###############################################################################################
    # Name: add_enumtype(enumtype)
    #   add (list append) a EnumType element to Schema element
    ###############################################################################################
    def add_enumtype(self, enumtype):
        self.EnumTypes.append(enumtype)

    ###############################################################################################
    # Name: add_action(action)
    #   add (list append) a Action element to Schema element
    ###############################################################################################
    def add_action(self, action):
        self.Actions.append(action)

    ###############################################################################################
    # Name: get_resource_type_obj_by_typename(typename)
    #   Takes a typename found in the resource type and searches within the Schema's Types to match
    #   the exact type it refers to. 
    #   Returns: 
    #       The type instance once matched
    ###############################################################################################
    # types can be structured/complex type, enumeration, actions
    def get_resource_type_obj_by_typename(self, typename):
        for et in self.EntityTypes:
            if et.Name == typename:
                return et

        for ct in self.ComplexTypes:
            if ct.Name == typename:
                return ct

        for ent in self.EnumTypes:
            if ent.Name == typename:
                return ent

        for action in self.Actions:
            if action.Name == typename:
                return action

        return None

    ###############################################################################################
    # Name: verify_resource_typename_in_schema(typename)
    #   Takes a typename found in the resource type (@odata.type) and searches within the Schema's 
    #   Types's Name to match if typename exists within the Schema element 
    #   Returns: 
    #       True if matched.
    ###############################################################################################
    # types can be structured/complex type, enumeration, actions
    def verify_resource_typename_in_schema(self, typename):

        for et in self.EntityTypes:
            if et.Name == typename:
                return True

        for ct in self.ComplexTypes:
            if ct.Name == typename:
                return True

        for ent in self.EnumTypes:
            if ent.Name == typename:
                return True

        for action in self.Actions:
            if action.Name == typename:
                return True

        return False


###################################################################################################
# Class CommonType:
#   This contains the common attributes in edm Elements EntityType and ComplexType. It contains
#   basetype, may contain one or more annotation elements, and two types of properties, i.e Element 
#   Property and NavigationProperty
###################################################################################################
class CommonType:
    def __init__(self, name, base_type=None): 
        self.Name = name
        self.BaseType = base_type
        self.Annotations = []
        self.Properties = []
        self.NavigationProperties = []   

    ###############################################################################################
    # Name: add_annotation(annotation)
    #   add (list append) a Annotation element to EntityType or ComplexType
    ###############################################################################################
    def add_annotation(self, annotation):
        self.Annotations.append(annotation)

    ###############################################################################################
    # Name: add_property(property)
    #   add (list append) a Property element to EntityType or ComplexType
    ###############################################################################################
    def add_property(self, property):
        self.Properties.append(property)

    ###############################################################################################
    # Name: add_navigationproperty(navigationproperty)
    #   add (list append) a NavigationProperty element to EntityType or ComplexType
    ###############################################################################################
    def add_navigationproperty(self, navigationproperty):
        self.NavigationProperties.append(navigationproperty)

    ###############################################################################################
    # Name: yeild_navigationproperty
    #   generator function to loop over NavigationProperties within Schema and yeild each instance 
    ###############################################################################################
    def yeild_navigationproperty(self):
        for nav_property in self.NavigationProperties:
            yield nav_property

###################################################################################################
# Class EntityType: Inherits from CommonType
#   This class represents the edm Element: EntityType. EntityType is within edm:Schema 
###################################################################################################
class EntityType(CommonType):
    pass

###################################################################################################
# Class ComplexType: Inherits from CommonType
#   This class represents the edm Element: ComplexType. ComplexType is within Schema Element.
###################################################################################################
class ComplexType(CommonType):
    pass
       
###################################################################################################
# Class Property:
#   This class represents the edm Element: Property. Property is within edm:EntityType and
#   edm:ComplexType. It contains a Type attribute and one or more annotation elements and a might
#   contain an attribute 'Nullable' if not, consider 'true' as its default value
###################################################################################################
class Property:
    def __init__(self, name, type, nullable='true'):
        self.Name = name
        self.Type = type
        self.Nullable = nullable
        self.Annotations = []

    ###############################################################################################
    # Name: add_annotation(annotation)
    #   add (list append) a Annotation element to Property
    ###############################################################################################
    def add_annotation(self, annotation):
        self.Annotations.append(annotation)

###################################################################################################
# Class NavigationProperty:
#   This class represents the edm Element: NavigationProperty. NavigationProperty is within 
#   edm:EntityType and edm:ComplexType. It contains attribute 'Type', might contain attributes 
#   'Nullable' and/or 'ContainsTarget' if not, consider 'true' and 'false' as their default values
#   respectively
###################################################################################################
class NavigationProperty:
    def __init__(self, name, type, contains_target='false', nullable = 'true'):
        self.Name = name
        self.Type = type
        self.Nullable = nullable
        self.Annotations = []
        self.ContainsTarget = contains_target 

    ###############################################################################################
    # Name: add_annotation(annotation)
    #   add (list append) a Annotation element to NavigationProperty
    ###############################################################################################
    def add_annotation(self, annotation):
        self.Annotations.append(annotation)

###################################################################################################
# Class EnumType:
#   This class represents the edm Element: EnumType. EnumType is within edm:Schema.
###################################################################################################
class EnumType:
    def __init__(self, name):
        self.Name = name
        self.Annotations = []
        self.Members = []

    ###############################################################################################
    # Name: add_member(enumtype)
    #   add (list append) a Member element to EnumType element
    ###############################################################################################
    def add_member(self, member):
        self.Members.append(member)

    ###############################################################################################
    # Name: add_annotation(annotation)
    #   add (list append) a Annotation element to EnumType
    ###############################################################################################
    def add_annotation(self, annotation):
        self.Annotations.append(annotation)

###################################################################################################
# Class Member:
#   This class represents the edm Element: Member. Member is within edm:EnumType.
###################################################################################################
class Member:
    def __init__(self, name):
        self.Name = name
        self.Annotations = []

    ###############################################################################################
    # Name: add_annotation(annotation)
    #   add (list append) a Annotation element to Member
    ###############################################################################################
    def add_annotation(self, annotation):
        self.Annotations.append(annotation)

###################################################################################################
# Class Action:
#   This class represents the edm Element: Action. Action is within edm:Schema.
###################################################################################################
class Action:
    def __init__(self, name, is_bool = None):
        self.Name = name
        self.IsBound = is_bool
        self.Annotations = []
        self.Parameters = []
 
    ###############################################################################################
    # Name: add_parameter(action)
    #   add (list append) a Paramter element to Action element
    ###############################################################################################
    def add_parameter(self, parameter):
        self.Parameters.append(parameter)

    ###############################################################################################
    # Name: add_annotation(annotation)
    #   add (list append) a Annotation element to Action
    ###############################################################################################
    def add_annotation(self, annotation):
        self.Annotations.append(annotation)

###################################################################################################       
# Class Parameter:
#   This class represents the edm Element: Parameter. Parameter is within edm:Action.
###################################################################################################
class Parameter:
    def __init__(self, name, type):
        self.Name = name
        self.Type = type
  
###################################################################################################
# Class Annotation:
#   This class represents the edm Element: Annotation. Annotations can be found in metadata elements 
#   such as entity type, complextype, property, action or parameter. Annotation applies a 'Term' to 
#   model an element. The Term may have attributes for a particular element for that Term which 
#   stored in this class as AttrKey and Constant Value 
###################################################################################################
class Annotation:
    def __init__(self, term = None, attr_key = None, attr_value = None):        
        self.Term = term
        self.AttrKey = attr_key
        self.AttrValue = attr_value
 
###################################################################################################
# Class: SchemaModel
#   This class contains functions to open the schema files and parse/serialize them into relevant 
#   structures defined in this module and collect them as a list. It also contains helper functions 
#   to search or verify certain things within the structures for the client tool.
#   Each instance of this class takes in an instance of logger module to keep track of warnings/
#   errors pertaining to Redfish Schema document.
###################################################################################################
class SchemaModel:
    def __init__(self, log = None):
        ## list Dataservices which is the Schema container within each Redfish Schema Document
        self.RedfishSchemas = [] 
        ## schemas with edmx + edm namespace context, starts with Edmx element
        self.FullRedfishSchemas = [] 
        ## list of Collection tpyes in the schemas
        self.collections = []
        self.log = log
        self.CommonRedfishResourceProperties = ['Id', 'Name', 'Description', 'Status', 'Links', 'Members', 'RelatedItem' , 'Actions', 'Oem' , 'OEM']

    ###############################################################################################
    # Name: map_element_to_csdlnamespace(element_tag)
    #   Takes in an 'element_tag' and maps it in csdlNamespace dict defined in this class
    # Return:
    #   returns a full tag name with csdl namespace prepended
    ###############################################################################################
    def map_element_to_csdlnamespace(self, element_tag):
        return csdlNamespace[element_tag] + element_tag

    ###############################################################################################
    # Name: verify_resource_metadata_reference(resource_namespace, resource_typename, metadata)
    #   Takes resource's namespace, its typename (@odata.type: namespace.typename) and the metadata 
    #   document serialized representation and verifies if the Resource's Type identifier is 
    #   referenced in or by $metadata. 
    #   Metadata document has element 'Reference' which is a uri reference of the schema document 
    #   of the resource. Within Reference, there are Include elements which contains the name of the
    #   namespaces that can be found within the refrenced schema document
    # Return:
    #   True if matched
    ###############################################################################################
    def verify_resource_metadata_reference(self, resource_namespace, resource_typename, metadata):
        for reference in metadata.References:
            for include in reference.Includes:
                ## Include contains of Namespaces, we need to check if the namespace of the resource matches any in the metadata document 
                if include.Namespace == resource_namespace:
                    ## if it does, we can use the Reference Uri to locate the schema file 
                    for rf_schema in self.RedfishSchemas:
                        dir, schema_name = os.path.split(rf_schema.SchemaUri)
                        if schema_name in reference.Uri:
                            ## once rf_schema file is located, we can verify if Type is referenced in or by the $metadata
                            for r_namespace in rf_schema.Schemas:
                                if r_namespace.Namespace == resource_namespace:
                                    if r_namespace.verify_resource_typename_in_schema(resource_typename):
                                        return True    
        return False

    ###############################################################################################
    # Name: verify_property_in_resource(xtype, property_name, resource_namespace)
    #   Takes in the Type instance that represents the resource in a schema document, which is of 
    #   EntityType or ComplexType, property name found in resources payload and its namespace found 
    #   in resource's Type identifier (@odata.type format: namespace.typename) and searches for a 
    #   key within all propreties of a Resource
    # Return:
    #   True if found 
    ###############################################################################################
    def verify_property_in_resource(self, xtype, property_name, resource_namespace = None):
        for property in xtype.Properties:
            if property.Name == property_name:
                return True

        for navproperty in xtype.NavigationProperties:
            if navproperty.Name == property_name:
                return True

        if resource_namespace:
            for complextype in resource_namespace.ComplexTypes:
                if complextype.Name == property_name:
                    return True
            ## also action?
            for action in resource_namespace.Actions:
                if action.Name  == property_name:
                    return True
        return False

    ###############################################################################################
    # Name: verify_property_in_resource_recur(xtype, property_name, resource_namespace)
    #   Takes in the Type instance that represents the resource in a schema document, which is of 
    #   EntityType or ComplexType, property name found in resources payload and its namespace found 
    #   in resource's Type identifier (@odata.type format: namespace.typename) and searches for a key
    #   within all propreties of a Resource. It recursively checks the resource using BaseType.  
    # Return:
    #   True if found 
    ###############################################################################################
    def verify_property_in_resource_recur(self, xtype, property_name, resource_namespace = None):
        for property in xtype.Properties:
            if property.Name == property_name:
                return True
        for navproperty in xtype.NavigationProperties:
            if navproperty.Name == property_name:
                return True

        if resource_namespace:
            for complextype in resource_namespace.ComplexTypes:
                if complextype.Name == property_name:
                    return True
 #Removing action as discussed with the Intel meeting - Fatima
            ## also action?
            '''
for action in resource_namespace.Actions:
                if action.Name  == property_name:
                    return True
'''
                 

        if xtype.BaseType:
            namespace_, typename_ = self.get_resource_namespace_typename(xtype.BaseType)
            if resource_namespace:
                return self.verify_property_in_resource_recur(typename_, property_name, namespace_)
            else:
                return self.verify_property_in_resource_recur(typename_, property_name)

        return False

    ###############################################################################################
    # Name: verify_resource_basetype(resource_type)
    #   Takes resource's type identifier (@odata.type or BaseType or Type format: namespace.typename) 
    #   and loops over all Schema Elements to match Namespace property against resource's namespace 
    #   and Types (Entity, Complex, Enum, Action) within the Schema element that was matched are 
    #   used to verify the typename.
    # Return:
    #   Boolean value for namespace and typename, True if found.
    ###############################################################################################
    def verify_resource_basetype(self, resource_type):
        namespace_found = False
        type_found = False
        if '#' in resource_type:
          resource_type = resource_type.split('#')[1]

        split_type = resource_type.rsplit('.', 1)
        if len(split_type) > 1:
            namespace = split_type[0]
            typename = split_type[1] 

            for rf_schema in self.RedfishSchemas:
                ns = rf_schema.find_ns_in_dataservices(namespace)
                if ns:
                    namespace_found = True
                    if ns.get_resource_type_obj_by_typename(typename):
                        type_found = True
                        return namespace_found, type_found
        
        return namespace_found, type_found


    ###############################################################################################
    # Name: get_resource_namespace_typename(resource_type)
    #   Takes the resource type identifier (@odata.type or BaseType or Type with format: 
    #   namespace.typename) and loops over all Schema Elements to match Namespace property against 
    #   resource's namespace and Types (Entity, Complex, Enum, Action) within the Schema element 
    #   that was matched are used to find the typename.
    # Return:
    #   instance of namespace and typename found within the schema documents
    ###############################################################################################
    def get_resource_namespace_typename(self, resource_type):       
        if '#' in resource_type:
            resource_type = resource_type.split('#')[1]

        split_type = resource_type.rsplit('.', 1)
        if len(split_type) > 1:
            namespace = split_type[0]
            typename = split_type[1] 

            for rf_schema in self.RedfishSchemas:
                namespace_ = rf_schema.find_ns_in_dataservices(namespace)
                if namespace_:
                    #find namespace
                    typename_ = namespace_.get_resource_type_obj_by_typename(typename)
                    if typename_:
                        return namespace_, typename_
                
        return None, None
    
    ###############################################################################################
    # Name: get_resource_typename(resource_type)
    #   Takes the resource type identifier (@odata.type or BaseType or Type with format: 
    #   namespace.typename) and loops over all Schema Elements to match Namespace property against 
    #   resource's namespace and Types (EntityType, ComplexType, Enum, Action) within the Schema
    #   element that was matched are used to find the typename.
    # Return:
    #   instance of typename found within the schema documents
    ###############################################################################################
    def get_resource_typename(self, resource_type):
        #define a primitive type, if type is in primitive type, skip this..
        primitive_types = ['Edm.Boolean', 'Edm.DateTimeOffset', 'Edm.Decimal', 'Edm.Double', 'Edm.Guid', 'Edm.Int64', 'Edm.String']
        if resource_type in primitive_types:
            return None
        else:
            # Collection is found aka NavigationProperty...
            if 'Collection(' in resource_type: 
               resource_type = resource_type[resource_type.find("(") + 1:resource_type.find(")")]
                            
            split_type = resource_type.rsplit('.', 1)
            if len(split_type) > 1:
                namespace = split_type[0]
                typename = split_type[1] 

                for rf_schema in self.RedfishSchemas:
                    ns = rf_schema.find_ns_in_dataservices(namespace)
                    if ns:
                        resource_type = ns.get_resource_type_obj_by_typename(typename)
                        return resource_type        
                                      
            return None

    ###############################################################################################
    # Name: verify_action_name_recur(namespace, typename, resource_action)
    #   Takes resource's namespace and typename extracted from resource's Type identifier 
    #   (@odata.type format namespace.typename) and resource's action property found in payload and 
    #   find action names within its namespace matching the action name found in the payload. 
    #   It recursively checks the resource using BaseType, if found in resource's typename.
    # Return:
    #   True, if matched
    ###############################################################################################
    def verify_action_name_recur(self, namespace, typename, resource_action):    
        if namespace.Actions:
            for action in namespace.Actions:
                contextprop_form = '#'+ namespace.Namespace +'.' + action.Name 
                if contextprop_form == resource_action:
                    return True
        else:
            if typename.BaseType:
                namespace_, typename_ = self.get_resource_namespace_typename(typename.BaseType)
                return self.verify_action_name_recur(namespace_, typename_, resource_action)

        return False

    ###############################################################################################
    # Name: verify_annotation(xelement, annotation_term)
    #   Takes in the metadata element 'xelement' which could be entity type, complextype, property, 
    #   action or parameter and an annotation Term, and verifies if annotation is present in element
    #   passed to the func
    # Return:
    #   True, if found
    ###############################################################################################
    def verify_annotation(self, xelement,  annotation_term):
        for annotation in xelement.Annotations:
            if annotation.Term == annotation_term:
                return True
        return False

    ###############################################################################################
    # Name: verify_annotation_recur(xelement, annotation_term)
    #   Takes in the metadata element 'xelement' which could be entity type, complextype, property, 
    #   action or parameter and an annotation Term, and verifies if annotation is present in element
    #   passed to the func. It recursively checks the resource using BaseType or Type if the element 
    #   (EntityType, ComplexType, Property, NavigationProperty) has any.
    # Return:
    #   True, if found
    ###############################################################################################
    def verify_annotation_recur(self, xelement, annotation_term):
        xelement_ = None

        for annotation in xelement.Annotations:
            if annotation.Term == annotation_term:
                 return True
                   
        #get infor on type first based on that recursion will follow
        if isinstance(xelement, (EntityType, ComplexType)):
            if xelement.BaseType:
                xelement_ = self.get_resource_typename(xelement.BaseType)
        # changed here to return False as it is not inherited.
        elif isinstance(xelement, (Property, NavigationProperty)):
            return False
            

        if xelement_:
            return self.verify_annotation_recur(xelement_, annotation_term)

        return False

    ###############################################################################################
    # Name: get_annotation(xelement, annotation_term)
    #   Takes in the metadata element 'xelement' which could be entity type, complextype, property, 
    #   action or parameter and an annotation Term, and verifies if annotation is present in element
    #   passed to the func
    # Return:
    #   instance of the annotation, if found
    ###############################################################################################
    def get_annotation(self, xelement, annotation_term):
        for annotation in xelement.Annotations:
            if annotation.Term == annotation_term:
                return annotation
        return None

    ###############################################################################################
    # Name: get_annotation_recur(xelement, annotation_term)
    #   Takes in the metadata element 'xelement' which could be entity type, complextype, property, 
    #   action or parameter and an annotation Term, and verifies if annotation is present in element
    #   passed to the func. It recursively checks the resource using BaseType or Type if the element 
    #   (EntityType, ComplexType, Property, NavigationProperty) has any.
    # Return:
    #   instance of the annotation, if found
    ###############################################################################################
    def get_annotation_recur(self, xelement, annotation_term):
        xelement_ = None

        for annotation in xelement.Annotations:
            if annotation.Term == annotation_term:
                 return annotation
                   
        #get infor on type first based on that recursion will follow
        if isinstance(xelement, (EntityType, ComplexType)):
            if xelement.BaseType:
                #verify annotation for base type in recursion
                xelement_ = self.get_resource_typename(xelement.BaseType)

        #changed to return to False, as it is not inherited.
        elif isinstance(xelement, (Property, NavigationProperty)):
            return False
            

        # if resource does not have an annotation within its own scope, check its
        # parents basetype's scope...
        if xelement_:
            return self.get_annotation_recur(xelement_, annotation_term)
                
    ###############################################################################################
    # All helper functions related to parsing schemas element tree and serializing them to their
    # objects
    ###############################################################################################
    # Name: parse_annotation_tag(edm_element) 
    #   Takes an edm element with entity type, complextype, property, action or parameter tags
    #   and finds all 'Annotation' tags nested within the edm element.
    # Return:
    #   yields the Term found within the Annotation Tag and Attribute key and value, if found 
    ###############################################################################################
    def parse_annotation_tag(self, edm_element):
        annotation_tag = self.map_element_to_csdlnamespace('Annotation')         
        for annotation in edm_element.findall(annotation_tag):
            annotation_term = None
            attr_key = None
            attr_value = None
            for key, value in annotation.items():
                if key == 'Term':
                    annotation_term = value
                else:
                    attr_key = key
                    attr_value = value

            yield annotation_term, attr_key, attr_value

    ###############################################################################################
    # Name: serialize_schema(schema_file = None, schema_payload= None, schema_url = None)
    #   Takes either xml schema document file or schema_payload w/schema_url. Parses it into an 
    #   Element tree structure to start serializing the xml from its root element (edmx namespace). 
    # Condition:
    #   File or payload MUST be in xml format, If it is unable to parse the file or payload into an
    #   Element tree, the tool exits reporting failure
    ###############################################################################################   
    def serialize_schema(self, schema_file = None, schema_payload= None, schema_uri = None):
        schema_root = None
        if schema_file:
            # parsing file to an element tree structure
            schema_etree = ET.parse(schema_file)
            if schema_etree is not None:
                try:
                    schema_root = schema_etree.getroot()
                except:
                    print('Could not parse element tree for its root element')
                    exit(0)
                else:                                            
                    self.serialize_edmx(schema_root, schema_file)

        elif schema_payload and schema_uri:
            schema_root = ET.fromstring(schema_payload.strip(b'\x00'))
            if schema_root is not None:
                self.serialize_edmx(schema_root, schema_uri)

        else:
            print('No data provided to serialize Redfish schemas')
            exit(0)

    ###############################################################################################
    # Name: serialize_edmx(schema_root, schema_uri)
    #   Takes schema root element to find edmx element, then serialize it according to csdl. Edmx 
    #   contains Edmx, Reference and DataServices. It appends the DataService element to RedfishSchema
    #   list
    # Returns:
    #   serialized edmx element
    ###############################################################################################   
    def serialize_edmx(self, schema_root, schema_uri):
        if 'Version' in schema_root.attrib:
            added_edmx = Edmx(schema_uri, schema_root.tag, schema_root.attrib['Version'])
        else:
            added_edmx = Edmx(schema_uri, schema_root.tag)
        print("\nroot element: %s" % schema_root.tag)
        print("root element attribute: %s" % schema_root.attrib)
        if added_edmx:           
            ## Full Redfish Schemas list containing every tag starting from <edmx>                            
            self.FullRedfishSchemas.append(added_edmx)
            # Parse nested tags...
            reference_tag = self.map_element_to_csdlnamespace('Reference')
            for reference in schema_root.findall(reference_tag):
                added_reference = Reference(reference.attrib['Uri'])
                # appends Reference to Edmx element 
                added_edmx.add_reference(added_reference)
                #has one or more nested include elements
                include_tag = self.map_element_to_csdlnamespace('Include')
                for include in reference.findall(include_tag):
                    if 'Alias' in include.attrib:
                        added_include = Include(include.attrib['Namespace'], include.attrib['Alias'])
                        # appends Include to Reference element
                        added_reference.add_include(added_include)
                    else:
                        added_include = Include(include.attrib['Namespace'])
                        # appends Include to Reference element
                        added_reference.add_include(added_include)  

            self.serialize_dataservices(schema_root, added_edmx, schema_uri)


    ###############################################################################################
    # Name: serialize_dataservices(schema_root, added_edmx, schema_uri)
    #   Takes xml root tag (edmx namespace) & instance of edmx element, finds dataservices element 
    #   within root tag, parses & serializes it according to csdl and appends DataServices element
    #   to Edmx element and to the RedfishSchemas list
    ###############################################################################################
    def serialize_dataservices(self, schema_root, added_edmx, schema_uri):
        ds = schema_root.find(self.map_element_to_csdlnamespace('DataServices'))
        added_dataservice = DataServices(schema_uri)
        if added_dataservice:
            ## Redfish Schemas list contain tag starting from <DataServices>
            self.RedfishSchemas.append(added_dataservice)
            added_edmx.add_dataservice(added_dataservice)
            schema_tag = self.map_element_to_csdlnamespace('Schema')
            for schema in ds.findall(schema_tag):
                # add namespaces to the schema container
                added_schema = Schema(schema.attrib['Namespace'], schema_uri)
                added_dataservice.add_schema(added_schema)
                print ("added namepace %s" % added_schema.Namespace)
                #serialize entitytypes within namespace
                self.serialize_entitytype(schema, added_schema)
                #serialize complextypes within namespace
                self.serialize_complextype(schema, added_schema)
                #serialize action within namespace
                self.serialize_action(schema, added_schema)
                #serialize enumtype within namespace
                self.serialize_enumtype(schema, added_schema)

    ###############################################################################################
    # Name: serialize_entitytype(schema, added_schema)
    #   Takes Schema tag and instance of Schema element, finds EntityType element within Schema tag, 
    #   parses & serializes it according to csdl and appends EntityType element to Schema element.
    ###############################################################################################
    def serialize_entitytype(self, schema, added_schema):
        entitytype_tag = self.map_element_to_csdlnamespace('EntityType')
        for et in schema.findall(entitytype_tag):
            if 'BaseType' in et.attrib:
                added_entity = EntityType(et.attrib['Name'], et.attrib['BaseType'])
                # add EntityType to a Schema element
                added_schema.add_entitytype(added_entity)    
            else:
                added_entity = EntityType(et.attrib['Name'])
                added_schema.add_entitytype(added_entity)

            if added_entity:
                #1.  annotation in entitytype
                annotation = self.parse_annotation_tag(et)
                for term, attr_key, attr_value in annotation:
                    added_annotation = Annotation(term, attr_key, attr_value)
                    added_entity.add_annotation(added_annotation)

                #2.  properties in entitytype
                self.serialize_property(et, added_entity)
               
                #3.navigationproperty in entitytype
                self.serialize_navigationproperty(et, added_entity)

            print("added EntityType: %s BaseType: %s to Namespace: %s" % (\
                                added_entity.Name,\
                                added_entity.BaseType,\
                                added_schema.Namespace))


    ###############################################################################################
    # Name: serialize_complextype(schema, added_schema)
    #   Takes Schema tag and instance of Schema element, finds ComplexType element within Schema tag, 
    #   parses & serializes it according to csdl and appends ComplexType element to Schema element.
    ###############################################################################################
    def serialize_complextype(self, schema, added_schema):
        complextype_tag = self.map_element_to_csdlnamespace('ComplexType')
        for ct in schema.findall(complextype_tag):
            if 'Name' in ct.attrib and 'BaseType' in ct.attrib:
                added_complextype = ComplexType(ct.attrib['Name'], ct.attrib['BaseType'])
                # add ComplexType to a Schema element
                added_schema.add_complextype(added_complextype)

            elif 'Name' in ct.attrib:
                added_complextype = ComplexType(ct.attrib['Name'])
                added_schema.add_complextype(added_complextype)

            if added_complextype:
                #1.  annotation in complextype
                annotation = self.parse_annotation_tag(ct)
                for term, attr_key, attr_value in annotation:    
                    added_annotation = Annotation(term, attr_key, attr_value)
                    added_complextype.add_annotation(added_annotation)
                #2.  properties in complextype
                self.serialize_property(ct, added_complextype)
                                                           
                #3.navigationproperty in complextype
                self.serialize_navigationproperty(ct, added_complextype)

            print("added ComplexType: %s BaseType: %s to Namespace: %s" % (\
                                                            added_complextype.Name,\
                                                            added_complextype.BaseType,\
                                                            added_schema.Namespace))  


    ###############################################################################################
    # Name: serialize_action(schema, added_schema)
    #   Takes Schema tag and instance of Schema element, finds Action element within Schema tag, 
    #   parses & serializes it according to csdl and appends Action element to Schema element.     
    ###############################################################################################
    def serialize_action(self, schema, added_schema):
        action_tag = self.map_element_to_csdlnamespace('Action')
        for action in schema.findall(action_tag):
            if 'IsBound' in action.attrib:
                added_action = Action(action.attrib['Name'], action.attrib['IsBound'])
            else:
                added_action = Action(action.attrib['Name'])
            # add action to Schema element
            added_schema.add_action(added_action)
            
            if added_action:
                #1.  annotations within action
                annotation = self.parse_annotation_tag(action)
                for term, attr_key, attr_value in annotation:    
                    added_annotation = Annotation(term, attr_key, attr_value)
                    added_action.add_annotation(added_annotation)

                #2.paramters within action 
                # annotation found in certain schemas within parameter but not specified in spec..
                parameter_tag = self.map_element_to_csdlnamespace('Parameter')
                for parameter in action.findall(parameter_tag):
                    added_parameter = Parameter(parameter.attrib['Name'], parameter.attrib['Type'])
                    added_action.add_parameter(added_parameter)

            print("added Action: %s to Namespace: %s" % (added_action.Name, added_schema.Namespace))
                      
    ###############################################################################################
    # Name: serialize_enumtype(schema, added_schema)
    #   Takes Schema tag and instance of Schema element, finds EnumType element within Schema tag, 
    #   parses & serializes it according to csdl and appends EnumType element to Schema element.
    ###############################################################################################               
    def serialize_enumtype(self, schema, added_schema):
        enumtype_tag = self.map_element_to_csdlnamespace('EnumType')
        for ent in schema.findall(enumtype_tag):
            added_enumtype = EnumType(ent.attrib['Name'])
            # add EnumType to Schema element
            added_schema.add_enumtype(added_enumtype)

            if added_enumtype:
                #1.  annotation in enumtype
                annotation = self.parse_annotation_tag(ent)
                for term, attr_key, attr_value in annotation:    
                    added_annotation = Annotation(term, attr_key, attr_value)
                    added_enumtype.add_annotation(added_annotation)

                #2.  members in enumtype
                member_tag = self.map_element_to_csdlnamespace('Member')
                for members in ent.findall(member_tag):
                    added_member = Member(members.attrib['Name'])
                    added_enumtype.add_member(added_member)

                    annotation = self.parse_annotation_tag(members)
                    for term, attr_key, attr_value in annotation:    
                        added_annotation = Annotation(term, attr_key, attr_value)
                        added_member.add_annotation(added_annotation)

            print("added EnumType: %s to Namespace %s" % (\
                                                            added_enumtype.Name,\
                                                            added_schema.Namespace))      
                

    ###############################################################################################
    # Name: serialize_navigationproperty(xtag, xtype)
    #   Takes xtag (EntityType or ComplexType) and its xtype instance, finds NavigationProperty 
    #   element nested in xtag, parses & serializes it according to csdl and appends 
    #   NavigationProperty element to xtype Element
    ###############################################################################################
    def serialize_navigationproperty(self, xtag, xtype):
        navigationproperty_tag = self.map_element_to_csdlnamespace('NavigationProperty')
        for navproperty in xtag.findall(navigationproperty_tag):
            if 'ContainsTarget' in navproperty.attrib and 'Nullable' in navproperty.attrib:
                added_navproperty = NavigationProperty(navproperty.attrib['Name'], navproperty.attrib['Type'], navproperty.attrib['ContainsTarget'], navproperty.attrib['Nullable'])
            elif 'ContainsTarget' in navproperty.attrib:
                added_navproperty = NavigationProperty(navproperty.attrib['Name'], navproperty.attrib['Type'], navproperty.attrib['ContainsTarget'])
            elif 'Nullable' in navproperty.attrib:
                added_navproperty = NavigationProperty(navproperty.attrib['Name'], navproperty.attrib['Type'], navproperty.attrib['Nullable'])
            else:
                added_navproperty = NavigationProperty(navproperty.attrib['Name'], navproperty.attrib['Type'])

            if 'Collection(' in navproperty.attrib['Type']:
                self.collections.append(navproperty.attrib['Type'])

            if added_navproperty:
                xtype.add_navigationproperty(added_navproperty)
                annotation = self.parse_annotation_tag(navproperty)
                for term, attr_key, attr_value in annotation:    
                    added_annotation = Annotation(term, attr_key, attr_value)
                    added_navproperty.add_annotation(added_annotation)

            '''
            print("added NavigationProperty: %s to Type %s" % (\
                                                            added_navproperty.Name,\
                                                            xtype.Name)) '''

    ###############################################################################################
    # Name: serialize_property(xtag, xtype)
    #   Takes xtag (EntityType or ComplexType) and its xtype instance, finds Property element nested 
    #   in xtag, parses & serializes it according to csdl and appends Property element to xtype
    #   Element
    ###############################################################################################
    def serialize_property(self, xtag, xtype):
        property_tag = self.map_element_to_csdlnamespace('Property') 
        for property in xtag.findall(property_tag):
            if 'Nullable' in property.attrib:
                added_property = Property(property.attrib['Name'], property.attrib['Type'], property.attrib['Nullable'])
            else:
                added_property = Property(property.attrib['Name'], property.attrib['Type'])

            if added_property:
                xtype.add_property(added_property)
                annotation = self.parse_annotation_tag(property)
                for term, attr_key, attr_value in annotation:    
                    added_annotation = Annotation(term, attr_key, attr_value)
                    added_property.add_annotation(added_annotation)
            '''
            print("added Property: %s to Type %s" % (added_property.Name,\
                                                            xtype.Name))'''



                    
