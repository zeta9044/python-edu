
###############################
# PostgreSQL
###############################

--------------------------------------------------------------------
-- First LEVEL : table -> object
-- Last  LEVEL : object -> table
--------------------------------------------------------------------
INSERT                                                                                                        
INTO AIS0113 ( /* infomatica.mappingGroup-QT_DF_MST_TBLMP#1 */                                                                                       
          PRJ_ID                , FILE_ID                 , SQL_ID                       , TABLE_ID               , COL_ID                                   
        , CALL_PRJ_ID           , CALL_FILE_ID            , CALL_SQL_ID                  , CALL_TABLE_ID          , CALL_COL_ID                              
        , OBJ_ID                , FUNC_ID                 , OWNER_NAME                   , TABLE_NAME             , CAPS_TABLE_NAME                          
        , SQL_OBJ_TYPE          , COL_NAME                , CAPS_COL_NAME                , COL_VALUE_YN           , COL_EXPR                                 
        , COL_NAME_ORG          , CAPS_COL_NAME_ORG       , CALL_OBJ_ID                  , CALL_FUNC_ID           , CALL_OWNER_NAME                          
        , CALL_TABLE_NAME       , CALL_CAPS_TABLE_NAME    , CALL_SQL_OBJ_TYPE            , CALL_COL_NAME          , CALL_CAPS_COL_NAME                       
        , CALL_COL_VALUE_YN     , CALL_COL_EXPR           , CALL_COL_NAME_ORG            , CALL_CAPS_COL_NAME_ORG , UNIQUE_OWNER_NAME                        
        , CALL_UNIQUE_OWNER_NAME, UNIQUE_OWNER_TGT_SRV_ID , CALL_UNIQUE_OWNER_TGT_SRV_ID , COND_MAPPING           , DATA_MAKER                               
        , MAPPING_KIND          , COL_ORDER_NO            , CALL_COL_ORDER_NO            , ADJ_COL_ORDER_NO       , CALL_ADJ_COL_ORDER_NO
        , SYSTEM_BIZ_ID         , CALL_SYSTEM_BIZ_ID )
with RECURSIVE taglist as ( 
select t.prj_id, t.file_id, t.tag_seq_id, t.parent_seq_id, t.tag_id, t.tag_name, t.line_no, t.column_no, concat('', t.tag_name) as tag_path
from ais0038 t
where t.prj_id = '61'
and t.parent_seq_id = -1
union all
select t.prj_id, t.file_id, t.tag_seq_id, t.parent_seq_id, t.tag_id, t.tag_name, t.line_no, t.column_no, concat(l.tag_path, '/', t.tag_name) as tag_path
from taglist l, ais0038 t 
where t.prj_id = l.prj_id
and t.file_id = l.file_id
and t.parent_seq_id = l.tag_seq_id
)
, workflow as ( -- workflow 정보 찾기
select w.file_id, a.attr_value || '_' || a2.attr_value work_name 
from taglist w, ais0039 a, taglist t, ais0039 a2, ais0039 a3
where w.tag_name = 'WORKFLOW'
and a.prj_id = w.prj_id
and a.file_id = w.file_id
and a.tag_seq_id = w.tag_seq_id
and a.attr_name = 'NAME'
and t.prj_id = w.prj_id
and t.file_id = w.file_id
and t.parent_seq_id = w.tag_seq_id
and t.tag_name = 'TASKINSTANCE'
and a2.prj_id = t.prj_id
and a2.file_id = t.file_id
and a2.tag_seq_id = t.tag_seq_id
and a2.attr_name = 'NAME'
and a3.prj_id = t.prj_id
and a3.file_id = t.file_id
and a3.tag_seq_id = t.tag_seq_id
and a3.attr_name = 'TASKTYPE'
and a3.attr_value in ('Session')
)
, shortcut as ( -- 소스/타겟명 찾기
select t.file_id, t.tag_seq_id sql_id, tt.tag_attr_seq_id tbl_id
	 , tt.attr_value as tbl_nm, w.work_name || '_' || so.attr_value as obj_nm, so.tag_seq_id obj_id, so.attr_value
from taglist t, ais0039 so, ais0039 tp, ais0039 tt, workflow w
where t.tag_name = 'SHORTCUT'
and so.prj_id = t.prj_id
and so.file_id = t.file_id
and so.tag_seq_id = t.tag_seq_id
and so.attr_name = 'NAME' -- object
and tp.prj_id = t.prj_id
and tp.file_id = t.file_id
and tp.tag_seq_id = t.tag_seq_id
and tp.attr_name = 'OBJECTTYPE'
and tp.attr_value in ('SOURCE', 'TARGET')
and tt.prj_id = t.prj_id
and tt.file_id = t.file_id
and tt.tag_seq_id = t.tag_seq_id
and tt.attr_name = 'REFOBJECTNAME' -- table
and w.file_id = t.file_id
--order by t.tag_seq_id, so.tag_attr_seq_id, t.line_no, t.column_no
)
-- First LEVEL : table -> object
select tt.prj_id          prj_id
	 , stc.file_id         file_id
	 , stc.sql_id          sql_id
	 , stc.tbl_id          tbl_id
	 , c.tag_attr_seq_id   col_id
	 , tt.prj_id          call_prj_id
	 , stc.file_id         call_file_id
	 , stc.sql_id          call_sql_id
	 , stc.obj_id          call_tbl_id
	 , c.tag_attr_seq_id   call_col_id
	 , 0                   obj_id
	 , 0                   func_id
	 , '[owner_undefined]' owner_name
	 , stc.tbl_nm          tbl_nm
	 , upper(stc.tbl_nm)   caps_tbl_nm
	 , 'tbl'               sql_obj_type
	 , c.attr_value        col_nm
	 , upper(c.attr_value) caps_col_nm
	 , 'N'                 call_value_yn
	 , c.attr_value        col_expr
	 , c.attr_value        col_nm_org
	 , upper(c.attr_value)   caps_col_nm_org
	 , 0                   call_obj_id
	 , 0                   call_func_id
	 , '[owner_undefined]' call_owner_name
	 , stc.obj_nm          call_tbl_nm
	 , upper(stc.obj_nm)   call_caps_tbl_nm
	 , 'obj'               call_sql_obj_type
	 , c.attr_value        call_col_nm
	 , upper(c.attr_value) call_caps_col_nm
	 , 'N'                 call_col_value_yn
	 , ''                  call_col_expr
	 , c.attr_value        call_col_name_org
	 , upper(c.attr_value) call_caps_col_nm_org
	 , '[owner_undefined]' unique_owner_name
	 , '[owner_undefined]' call_unique_owner_name
	 , '[owner_undefined]' unique_owner_tgt_srv_id
	 , '[owner_undefined]' call_unique_owner_tgt_srv_id
	 , 1                   cond_mapping
	 , 2000                data_maker
	 , null                MAPPING_KIND
	 , ROW_NUMBER() OVER(order by c.line_no) col_order_no
	 , ROW_NUMBER() OVER(order by c.line_no) call_col_order_no
	 , ROW_NUMBER() OVER(order by c.line_no) adj_col_order_no
	 , ROW_NUMBER() OVER(order by c.line_no) call_adj_col_order_no
	 , '[owner_undefined]' as SYSTEM_BIZ_ID
     , '[owner_undefined]' as CALL_SYSTEM_BIZ_ID
--stc.tbl_nm src_tbl_nm, c.attr_value src_col_nm, stc.obj_nm tgt_obj_nm, c.attr_value tgt_col_nm, c.line_no
from shortcut stc, taglist t, ais0039 tt, taglist ct, ais0039 c
where t.file_id = stc.file_id 
and t.tag_name = 'SOURCE'
and tt.prj_id = t.prj_id
and tt.file_id = t.file_id
and tt.tag_seq_id = t.tag_seq_id
and tt.attr_name = 'NAME' -- source table
and tt.attr_value = stc.tbl_nm
and ct.file_id = t.file_id
and ct.parent_seq_id = t.tag_seq_id
and ct.tag_name = 'SOURCEFIELD'
and c.prj_id = ct.prj_id
and c.file_id = ct.file_id
and c.tag_seq_id = ct.tag_seq_id
and c.attr_name = 'NAME'
union all
-- Last  LEVEL : object -> table
select tt.prj_id          prj_id
	 , stc.file_id         file_id
	 , stc.sql_id          sql_id
	 , stc.obj_id          tbl_id
	 , c.tag_attr_seq_id   col_id
	 , tt.prj_id          call_prj_id
	 , stc.file_id         call_file_id
	 , stc.sql_id          call_sql_id
	 , stc.tbl_id          call_tbl_id
	 , c.tag_attr_seq_id   call_col_id
	 , 0                   obj_id
	 , 0                   func_id
	 , '[owner_undefined]' owner_name
	 , stc.obj_nm          tbl_nm
	 , upper(stc.obj_nm)   caps_tbl_nm
	 , 'obj'               sql_obj_type
	 , c.attr_value        col_nm
	 , upper(c.attr_value) caps_col_nm
	 , 'N'                 call_value_yn
	 , c.attr_value        col_expr
	 , c.attr_value        col_nm_org
	 , upper(c.attr_value)   caps_col_nm_org
	 , 0                   call_obj_id
	 , 0                   call_func_id
	 , '[owner_undefined]' call_owner_name
	 , stc.tbl_nm          call_tbl_nm
	 , upper(stc.tbl_nm)   call_caps_tbl_nm
	 , 'tbl'               call_sql_obj_type
	 , c.attr_value        call_col_nm
	 , upper(c.attr_value) call_caps_col_nm
	 , 'N'                 call_col_value_yn
	 , ''                  call_col_expr
	 , c.attr_value        call_col_name_org
	 , upper(c.attr_value) call_caps_col_nm_org
	 , '[owner_undefined]' unique_owner_name
	 , '[owner_undefined]' call_unique_owner_name
	 , '[owner_undefined]' unique_owner_tgt_srv_id
	 , '[owner_undefined]' call_unique_owner_tgt_srv_id
	 , 1                   cond_mapping
	 , 2000                data_maker
	 , null                MAPPING_KIND
	 , ROW_NUMBER() OVER(order by c.line_no) col_order_no
	 , ROW_NUMBER() OVER(order by c.line_no) call_col_order_no
	 , ROW_NUMBER() OVER(order by c.line_no) adj_col_order_no
	 , ROW_NUMBER() OVER(order by c.line_no) call_adj_col_order_no
	 , '[owner_undefined]' as SYSTEM_BIZ_ID
     , '[owner_undefined]' as CALL_SYSTEM_BIZ_ID
--     stc.obj_nm src_obj_nm, c.attr_value src_col_nm, stc.tbl_nm tgt_tbl_nm, c.attr_value tgt_col_nm, c.line_no
from shortcut stc, taglist t, ais0039 tt, taglist ct, ais0039 c
where t.file_id = stc.file_id 
and t.tag_name = 'TARGET'
and tt.prj_id = t.prj_id
and tt.file_id = t.file_id
and tt.tag_seq_id = t.tag_seq_id
and tt.attr_name = 'NAME' -- target table
and tt.attr_value = stc.tbl_nm
and ct.file_id = t.file_id
and ct.parent_seq_id = t.tag_seq_id
and ct.tag_name = 'TARGETFIELD'
and c.prj_id = ct.prj_id
and c.file_id = ct.file_id
and c.tag_seq_id = ct.tag_seq_id
and c.attr_name = 'NAME'


--------------------------------------------------------------------
-- midlle LEVELs : object -> object
--------------------------------------------------------------------
INSERT                                                                                                        
INTO AIS0113 ( /* infomatica.mappingGroup-QT_DF_MST_TBLMP#2 */                                                                                       
          PRJ_ID                , FILE_ID                 , SQL_ID                       , TABLE_ID               , COL_ID                                   
        , CALL_PRJ_ID           , CALL_FILE_ID            , CALL_SQL_ID                  , CALL_TABLE_ID          , CALL_COL_ID                              
        , OBJ_ID                , FUNC_ID                 , OWNER_NAME                   , TABLE_NAME             , CAPS_TABLE_NAME                          
        , SQL_OBJ_TYPE          , COL_NAME                , CAPS_COL_NAME                , COL_VALUE_YN           , COL_EXPR                                 
        , COL_NAME_ORG          , CAPS_COL_NAME_ORG       , CALL_OBJ_ID                  , CALL_FUNC_ID           , CALL_OWNER_NAME                          
        , CALL_TABLE_NAME       , CALL_CAPS_TABLE_NAME    , CALL_SQL_OBJ_TYPE            , CALL_COL_NAME          , CALL_CAPS_COL_NAME                       
        , CALL_COL_VALUE_YN     , CALL_COL_EXPR           , CALL_COL_NAME_ORG            , CALL_CAPS_COL_NAME_ORG , UNIQUE_OWNER_NAME                        
        , CALL_UNIQUE_OWNER_NAME, UNIQUE_OWNER_TGT_SRV_ID , CALL_UNIQUE_OWNER_TGT_SRV_ID , COND_MAPPING           , DATA_MAKER                               
        , MAPPING_KIND          , COL_ORDER_NO            , CALL_COL_ORDER_NO            , ADJ_COL_ORDER_NO       , CALL_ADJ_COL_ORDER_NO
        , SYSTEM_BIZ_ID         , CALL_SYSTEM_BIZ_ID )
with RECURSIVE taglist as (
select t.prj_id, t.file_id, t.tag_seq_id, t.parent_seq_id, t.tag_id, t.tag_name, t.line_no, t.column_no, concat('', t.tag_name) as tag_path
from ais0038 t
where t.prj_id = '61'
and t.parent_seq_id = -1
union all
select t.prj_id, t.file_id, t.tag_seq_id, t.parent_seq_id, t.tag_id, t.tag_name, t.line_no, t.column_no, concat(l.tag_path, '/', t.tag_name) as tag_path
from taglist l, ais0038 t 
where t.prj_id = l.prj_id
and t.file_id = l.file_id
and t.parent_seq_id = l.tag_seq_id
)
, workflow as ( -- workflow 정보 찾기
select w.file_id, a.attr_value || '_' || a2.attr_value || '_' work_name 
from taglist w, ais0039 a, taglist t, ais0039 a2, ais0039 a3
where w.tag_name = 'WORKFLOW'
and a.prj_id = w.prj_id
and a.file_id = w.file_id
and a.tag_seq_id = w.tag_seq_id
and a.attr_name = 'NAME'
and t.prj_id = w.prj_id
and t.file_id = w.file_id
and t.parent_seq_id = w.tag_seq_id
and t.tag_name = 'TASKINSTANCE'
and a2.prj_id = t.prj_id
and a2.file_id = t.file_id
and a2.tag_seq_id = t.tag_seq_id
and a2.attr_name = 'NAME'
and a3.prj_id = t.prj_id
and a3.file_id = t.file_id
and a3.tag_seq_id = t.tag_seq_id
and a3.attr_name = 'TASKTYPE'
and a3.attr_value in ('Session')
)
select t.prj_id          prj_id
	 , t.file_id         file_id
	 , t.tag_seq_id          sql_id
	 , so.tag_seq_id          tbl_id
	 , sf.tag_attr_seq_id   col_id
	 , tgt.prj_id          call_prj_id
	 , tgt.file_id         call_file_id
	 , t.tag_seq_id          call_sql_id
	 , tgt.tag_seq_id          call_tbl_id
	 , tf.tag_attr_seq_id   call_col_id
	 , 0                   obj_id
	 , 0                   func_id
	 , '[owner_undefined]' owner_name
	 , w.work_name || so.attr_value          tbl_nm
	 , upper(w.work_name || so.attr_value)   caps_tbl_nm
	 , 'obj'               sql_obj_type
	 , sf.attr_value        col_nm
	 , upper(sf.attr_value) caps_col_nm
	 , 'N'                 call_value_yn
	 , sf.attr_value        col_expr
	 , sf.attr_value        col_nm_org
	 , upper(sf.attr_value)   caps_col_nm_org
	 , 0                   call_obj_id
	 , 0                   call_func_id
	 , '[owner_undefined]' call_owner_name
	 , w.work_name || tgt.attr_value          call_tbl_nm
	 , upper(w.work_name || tgt.attr_value)   call_caps_tbl_nm
	 , 'obj'               call_sql_obj_type
	 , tf.attr_value        call_col_nm
	 , upper(tf.attr_value) call_caps_col_nm
	 , 'N'                 call_col_value_yn
	 , ''                  call_col_expr
	 , tf.attr_value        call_col_name_org
	 , upper(tf.attr_value) call_caps_col_nm_org
	 , '[owner_undefined]' unique_owner_name
	 , '[owner_undefined]' call_unique_owner_name
	 , '[owner_undefined]' unique_owner_tgt_srv_id
	 , '[owner_undefined]' call_unique_owner_tgt_srv_id
	 , 1                   cond_mapping
	 , 2001                data_maker
	 , null                MAPPING_KIND
	 , ROW_NUMBER() OVER(order by sf.line_no) col_order_no
	 , ROW_NUMBER() OVER(order by tf.line_no) call_col_order_no
	 , ROW_NUMBER() OVER(order by sf.line_no) adj_col_order_no
	 , ROW_NUMBER() OVER(order by tf.line_no) call_adj_col_order_no
	 , '[owner_undefined]' as SYSTEM_BIZ_ID
     , '[owner_undefined]' as CALL_SYSTEM_BIZ_ID
--select w.work_name || so.attr_value src_obj_nm, sf.attr_value src_fld_nm, w.work_name || tgt.attr_value tgt_obj_nm, tf.attr_value tgt_fld_nm
from workflow w, taglist t, ais0039 so, ais0039 sf, ais0039 as tgt, ais0039 tf
where t.file_id = w.file_id
and t.tag_path = 'POWERMART/REPOSITORY/FOLDER/MAPPING/CONNECTOR'
and so.prj_id = t.prj_id
and so.file_id = t.file_id
and so.tag_seq_id = t.tag_seq_id
and so.attr_name = 'FROMINSTANCE'
and sf.prj_id = t.prj_id
and sf.file_id = t.file_id
and sf.tag_seq_id = t.tag_seq_id
and sf.attr_name = 'FROMFIELD'
and tgt.prj_id = t.prj_id
and tgt.file_id = t.file_id
and tgt.tag_seq_id = t.tag_seq_id
and tgt.attr_name = 'TOINSTANCE'
and tf.prj_id = t.prj_id
and tf.file_id = t.file_id
and tf.tag_seq_id = t.tag_seq_id
and tf.attr_name = 'TOFIELD'



###############################
# Oracle
###############################

--------------------------------------------------------------------
-- First LEVEL : table -> object
--------------------------------------------------------------------
INSERT                                                                                                        
INTO AIS0113 ( /* infomatica.mappingGroup-QT_DF_MST_TBLMP#1 */                                                                                       
          PRJ_ID                , FILE_ID                 , SQL_ID                       , TABLE_ID               , COL_ID                                   
        , CALL_PRJ_ID           , CALL_FILE_ID            , CALL_SQL_ID                  , CALL_TABLE_ID          , CALL_COL_ID                              
        , OBJ_ID                , FUNC_ID                 , OWNER_NAME                   , TABLE_NAME             , CAPS_TABLE_NAME                          
        , SQL_OBJ_TYPE          , COL_NAME                , CAPS_COL_NAME                , COL_VALUE_YN           , COL_EXPR                                 
        , COL_NAME_ORG          , CAPS_COL_NAME_ORG       , CALL_OBJ_ID                  , CALL_FUNC_ID           , CALL_OWNER_NAME                          
        , CALL_TABLE_NAME       , CALL_CAPS_TABLE_NAME    , CALL_SQL_OBJ_TYPE            , CALL_COL_NAME          , CALL_CAPS_COL_NAME                       
        , CALL_COL_VALUE_YN     , CALL_COL_EXPR           , CALL_COL_NAME_ORG            , CALL_CAPS_COL_NAME_ORG , UNIQUE_OWNER_NAME                        
        , CALL_UNIQUE_OWNER_NAME, UNIQUE_OWNER_TGT_SRV_ID , CALL_UNIQUE_OWNER_TGT_SRV_ID , COND_MAPPING           , DATA_MAKER                               
        , MAPPING_KIND          , COL_ORDER_NO            , CALL_COL_ORDER_NO            , ADJ_COL_ORDER_NO       , CALL_ADJ_COL_ORDER_NO
        , SYSTEM_BIZ_ID         , CALL_SYSTEM_BIZ_ID )
        
with taglist(prj_id, file_id, tag_seq_id, parent_seq_id, tag_id, tag_name, line_no, column_no, tag_path) 
as ( 
select t.prj_id, t.file_id, t.tag_seq_id, t.parent_seq_id, t.tag_id, t.tag_name, t.line_no, t.column_no, t.tag_name as tag_path
from ais0038 t
where t.prj_id = ##{{prj_id}} --'1283'
and t.parent_seq_id = -1
union all
select t.prj_id, t.file_id, t.tag_seq_id, t.parent_seq_id, t.tag_id, t.tag_name, t.line_no, t.column_no, l.tag_path||'/'||t.tag_name as tag_path
from taglist l, ais0038 t 
where t.prj_id = l.prj_id
and t.file_id = l.file_id
and t.parent_seq_id = l.tag_seq_id
)
, workflow as ( -- workflow 정보 찾기
select w.file_id, a.attr_value || '_' || a2.attr_value work_name 
from taglist w, ais0039 a, taglist t, ais0039 a2, ais0039 a3
where w.tag_name = 'WORKFLOW'
and a.prj_id = w.prj_id
and a.file_id = w.file_id
and a.tag_seq_id = w.tag_seq_id
and a.attr_name = 'NAME'
and t.prj_id = w.prj_id
and t.file_id = w.file_id
and t.parent_seq_id = w.tag_seq_id
and t.tag_name = 'TASKINSTANCE'
and a2.prj_id = t.prj_id
and a2.file_id = t.file_id
and a2.tag_seq_id = t.tag_seq_id
and a2.attr_name = 'NAME'
and a3.prj_id = t.prj_id
and a3.file_id = t.file_id
and a3.tag_seq_id = t.tag_seq_id
and a3.attr_name = 'TASKTYPE'
and a3.attr_value in ('Session')
)
, shortcut as ( -- 소스/타겟명 찾기
select t.file_id, t.tag_seq_id sql_id, tt.tag_attr_seq_id tbl_id
	 , tt.attr_value as tbl_nm, w.work_name || '_' || so.attr_value as obj_nm, so.tag_seq_id obj_id, so.attr_value
from taglist t, ais0039 so, ais0039 tp, ais0039 tt, workflow w
where t.tag_name = 'SHORTCUT'
and so.prj_id = t.prj_id
and so.file_id = t.file_id
and so.tag_seq_id = t.tag_seq_id
and so.attr_name = 'NAME' -- object
and tp.prj_id = t.prj_id
and tp.file_id = t.file_id
and tp.tag_seq_id = t.tag_seq_id
and tp.attr_name = 'OBJECTTYPE'
and tp.attr_value in ('SOURCE', 'TARGET')
and tt.prj_id = t.prj_id
and tt.file_id = t.file_id
and tt.tag_seq_id = t.tag_seq_id
and tt.attr_name = 'REFOBJECTNAME' -- table
and w.file_id = t.file_id
--order by t.tag_seq_id, so.tag_attr_seq_id, t.line_no, t.column_no
)
-- First LEVEL : table -> object
select tt.prj_id          prj_id
	 , stc.file_id         file_id
	 , stc.sql_id          sql_id
	 , stc.tbl_id          tbl_id
	 , c.tag_attr_seq_id   col_id
	 , tt.prj_id          call_prj_id
	 , stc.file_id         call_file_id
	 , stc.sql_id          call_sql_id
	 , stc.obj_id          call_tbl_id
	 , c.tag_attr_seq_id   call_col_id
	 , 0                   obj_id
	 , 0                   func_id
	 , '[owner_undefined]' owner_name
	 , stc.tbl_nm          tbl_nm
	 , upper(stc.tbl_nm)   caps_tbl_nm
	 , 'tbl'               sql_obj_type
	 , c.attr_value        col_nm
	 , upper(c.attr_value) caps_col_nm
	 , 'N'                 call_value_yn
	 , c.attr_value        col_expr
	 , c.attr_value        col_nm_org
	 , upper(c.attr_value)   caps_col_nm_org
	 , 0                   call_obj_id
	 , 0                   call_func_id
	 , '[owner_undefined]' call_owner_name
	 , stc.obj_nm          call_tbl_nm
	 , upper(stc.obj_nm)   call_caps_tbl_nm
	 , 'obj'               call_sql_obj_type
	 , c.attr_value        call_col_nm
	 , upper(c.attr_value) call_caps_col_nm
	 , 'N'                 call_col_value_yn
	 , ''                  call_col_expr
	 , c.attr_value        call_col_name_org
	 , upper(c.attr_value) call_caps_col_nm_org
	 , '[owner_undefined]' unique_owner_name
	 , '[owner_undefined]' call_unique_owner_name
	 , '[owner_undefined]' unique_owner_tgt_srv_id
	 , '[owner_undefined]' call_unique_owner_tgt_srv_id
	 , 1                   cond_mapping
	 , 2000                data_maker
	 , null                MAPPING_KIND
	 , ROW_NUMBER() OVER(order by c.line_no) col_order_no
	 , ROW_NUMBER() OVER(order by c.line_no) call_col_order_no
	 , ROW_NUMBER() OVER(order by c.line_no) adj_col_order_no
	 , ROW_NUMBER() OVER(order by c.line_no) call_adj_col_order_no
	 , '[owner_undefined]' as SYSTEM_BIZ_ID
     , '[owner_undefined]' as CALL_SYSTEM_BIZ_ID
--stc.tbl_nm src_tbl_nm, c.attr_value src_col_nm, stc.obj_nm tgt_obj_nm, c.attr_value tgt_col_nm, c.line_no
from shortcut stc, taglist t, ais0039 tt, taglist ct, ais0039 c
where t.file_id = stc.file_id 
and t.tag_name = 'SOURCE'
and tt.prj_id = t.prj_id
and tt.file_id = t.file_id
and tt.tag_seq_id = t.tag_seq_id
and tt.attr_name = 'NAME' -- source table
and tt.attr_value = stc.tbl_nm
and ct.file_id = t.file_id
and ct.parent_seq_id = t.tag_seq_id
and ct.tag_name = 'SOURCEFIELD'
and c.prj_id = ct.prj_id
and c.file_id = ct.file_id
and c.tag_seq_id = ct.tag_seq_id
and c.attr_name = 'NAME';

--------------------------------------------------------------------
-- midlle LEVELs : object -> object
--------------------------------------------------------------------
INSERT                                                                                                        
INTO AIS0113 ( /* infomatica.mappingGroup-QT_DF_MST_TBLMP#2 */                                                                                       
          PRJ_ID                , FILE_ID                 , SQL_ID                       , TABLE_ID               , COL_ID                                   
        , CALL_PRJ_ID           , CALL_FILE_ID            , CALL_SQL_ID                  , CALL_TABLE_ID          , CALL_COL_ID                              
        , OBJ_ID                , FUNC_ID                 , OWNER_NAME                   , TABLE_NAME             , CAPS_TABLE_NAME                          
        , SQL_OBJ_TYPE          , COL_NAME                , CAPS_COL_NAME                , COL_VALUE_YN           , COL_EXPR                                 
        , COL_NAME_ORG          , CAPS_COL_NAME_ORG       , CALL_OBJ_ID                  , CALL_FUNC_ID           , CALL_OWNER_NAME                          
        , CALL_TABLE_NAME       , CALL_CAPS_TABLE_NAME    , CALL_SQL_OBJ_TYPE            , CALL_COL_NAME          , CALL_CAPS_COL_NAME                       
        , CALL_COL_VALUE_YN     , CALL_COL_EXPR           , CALL_COL_NAME_ORG            , CALL_CAPS_COL_NAME_ORG , UNIQUE_OWNER_NAME                        
        , CALL_UNIQUE_OWNER_NAME, UNIQUE_OWNER_TGT_SRV_ID , CALL_UNIQUE_OWNER_TGT_SRV_ID , COND_MAPPING           , DATA_MAKER                               
        , MAPPING_KIND          , COL_ORDER_NO            , CALL_COL_ORDER_NO            , ADJ_COL_ORDER_NO       , CALL_ADJ_COL_ORDER_NO
        , SYSTEM_BIZ_ID         , CALL_SYSTEM_BIZ_ID )
with taglist(prj_id, file_id, tag_seq_id, parent_seq_id, tag_id, tag_name, line_no, column_no, tag_path) 
as (
select t.prj_id, t.file_id, t.tag_seq_id, t.parent_seq_id, t.tag_id, t.tag_name, t.line_no, t.column_no, t.tag_name as tag_path
from ais0038 t
where t.prj_id = ##{{prj_id}} --'1283'
and t.parent_seq_id = -1
union all
select t.prj_id, t.file_id, t.tag_seq_id, t.parent_seq_id, t.tag_id, t.tag_name, t.line_no, t.column_no, l.tag_path||'/'||t.tag_name as tag_path
from taglist l, ais0038 t 
where t.prj_id = l.prj_id
and t.file_id = l.file_id
and t.parent_seq_id = l.tag_seq_id
)
, workflow as ( -- workflow 정보 찾기
select w.file_id, a.attr_value || '_' || a2.attr_value || '_' work_name 
from taglist w, ais0039 a, taglist t, ais0039 a2, ais0039 a3
where w.tag_name = 'WORKFLOW'
and a.prj_id = w.prj_id
and a.file_id = w.file_id
and a.tag_seq_id = w.tag_seq_id
and a.attr_name = 'NAME'
and t.prj_id = w.prj_id
and t.file_id = w.file_id
and t.parent_seq_id = w.tag_seq_id
and t.tag_name = 'TASKINSTANCE'
and a2.prj_id = t.prj_id
and a2.file_id = t.file_id
and a2.tag_seq_id = t.tag_seq_id
and a2.attr_name = 'NAME'
and a3.prj_id = t.prj_id
and a3.file_id = t.file_id
and a3.tag_seq_id = t.tag_seq_id
and a3.attr_name = 'TASKTYPE'
and a3.attr_value in ('Session')
)
select t.prj_id          prj_id
	 , t.file_id         file_id
	 , t.tag_seq_id          sql_id
	 , so.tag_seq_id          tbl_id
	 , sf.tag_attr_seq_id   col_id
	 , tgt.prj_id          call_prj_id
	 , tgt.file_id         call_file_id
	 , t.tag_seq_id          call_sql_id
	 , tgt.tag_seq_id          call_tbl_id
	 , tf.tag_attr_seq_id   call_col_id
	 , 0                   obj_id
	 , 0                   func_id
	 , '[owner_undefined]' owner_name
	 , w.work_name || so.attr_value          tbl_nm
	 , upper(w.work_name || so.attr_value)   caps_tbl_nm
	 , 'obj'               sql_obj_type
	 , sf.attr_value        col_nm
	 , upper(sf.attr_value) caps_col_nm
	 , 'N'                 call_value_yn
	 , sf.attr_value        col_expr
	 , sf.attr_value        col_nm_org
	 , upper(sf.attr_value)   caps_col_nm_org
	 , 0                   call_obj_id
	 , 0                   call_func_id
	 , '[owner_undefined]' call_owner_name
	 , w.work_name || tgt.attr_value          call_tbl_nm
	 , upper(w.work_name || tgt.attr_value)   call_caps_tbl_nm
	 , 'obj'               call_sql_obj_type
	 , tf.attr_value        call_col_nm
	 , upper(tf.attr_value) call_caps_col_nm
	 , 'N'                 call_col_value_yn
	 , ''                  call_col_expr
	 , tf.attr_value        call_col_name_org
	 , upper(tf.attr_value) call_caps_col_nm_org
	 , '[owner_undefined]' unique_owner_name
	 , '[owner_undefined]' call_unique_owner_name
	 , '[owner_undefined]' unique_owner_tgt_srv_id
	 , '[owner_undefined]' call_unique_owner_tgt_srv_id
	 , 1                   cond_mapping
	 , 2001                data_maker
	 , null                MAPPING_KIND
	 , ROW_NUMBER() OVER(order by sf.line_no) col_order_no
	 , ROW_NUMBER() OVER(order by tf.line_no) call_col_order_no
	 , ROW_NUMBER() OVER(order by sf.line_no) adj_col_order_no
	 , ROW_NUMBER() OVER(order by tf.line_no) call_adj_col_order_no
	 , '[owner_undefined]' as SYSTEM_BIZ_ID
     , '[owner_undefined]' as CALL_SYSTEM_BIZ_ID
--select w.work_name || so.attr_value src_obj_nm, sf.attr_value src_fld_nm, w.work_name || tgt.attr_value tgt_obj_nm, tf.attr_value tgt_fld_nm
from workflow w, taglist t, ais0039 so, ais0039 sf, ais0039 tgt, ais0039 tf
where t.file_id = w.file_id
and t.tag_path = 'POWERMART/REPOSITORY/FOLDER/MAPPING/CONNECTOR'
and so.prj_id = t.prj_id
and so.file_id = t.file_id
and so.tag_seq_id = t.tag_seq_id
and so.attr_name = 'FROMINSTANCE'
and sf.prj_id = t.prj_id
and sf.file_id = t.file_id
and sf.tag_seq_id = t.tag_seq_id
and sf.attr_name = 'FROMFIELD'
and tgt.prj_id = t.prj_id
and tgt.file_id = t.file_id
and tgt.tag_seq_id = t.tag_seq_id
and tgt.attr_name = 'TOINSTANCE'
and tf.prj_id = t.prj_id
and tf.file_id = t.file_id
and tf.tag_seq_id = t.tag_seq_id
and tf.attr_name = 'TOFIELD';




--------------------------------------------------------------------
-- Last  LEVEL : object -> table
--------------------------------------------------------------------
INSERT                                                                                                        
INTO AIS0113 ( /* infomatica.mappingGroup-QT_DF_MST_TBLMP#3 */                                                                                       
          PRJ_ID                , FILE_ID                 , SQL_ID                       , TABLE_ID               , COL_ID                                   
        , CALL_PRJ_ID           , CALL_FILE_ID            , CALL_SQL_ID                  , CALL_TABLE_ID          , CALL_COL_ID                              
        , OBJ_ID                , FUNC_ID                 , OWNER_NAME                   , TABLE_NAME             , CAPS_TABLE_NAME                          
        , SQL_OBJ_TYPE          , COL_NAME                , CAPS_COL_NAME                , COL_VALUE_YN           , COL_EXPR                                 
        , COL_NAME_ORG          , CAPS_COL_NAME_ORG       , CALL_OBJ_ID                  , CALL_FUNC_ID           , CALL_OWNER_NAME                          
        , CALL_TABLE_NAME       , CALL_CAPS_TABLE_NAME    , CALL_SQL_OBJ_TYPE            , CALL_COL_NAME          , CALL_CAPS_COL_NAME                       
        , CALL_COL_VALUE_YN     , CALL_COL_EXPR           , CALL_COL_NAME_ORG            , CALL_CAPS_COL_NAME_ORG , UNIQUE_OWNER_NAME                        
        , CALL_UNIQUE_OWNER_NAME, UNIQUE_OWNER_TGT_SRV_ID , CALL_UNIQUE_OWNER_TGT_SRV_ID , COND_MAPPING           , DATA_MAKER                               
        , MAPPING_KIND          , COL_ORDER_NO            , CALL_COL_ORDER_NO            , ADJ_COL_ORDER_NO       , CALL_ADJ_COL_ORDER_NO
        , SYSTEM_BIZ_ID         , CALL_SYSTEM_BIZ_ID )
with taglist(prj_id, file_id, tag_seq_id, parent_seq_id, tag_id, tag_name, line_no, column_no, tag_path) 
as ( 
select t.prj_id, t.file_id, t.tag_seq_id, t.parent_seq_id, t.tag_id, t.tag_name, t.line_no, t.column_no, t.tag_name as tag_path
from ais0038 t
where t.prj_id = ##{{prj_id}} --'1283'
and t.parent_seq_id = -1
union all
select t.prj_id, t.file_id, t.tag_seq_id, t.parent_seq_id, t.tag_id, t.tag_name, t.line_no, t.column_no, l.tag_path||'/'||t.tag_name as tag_path
from taglist l, ais0038 t 
where t.prj_id = l.prj_id
and t.file_id = l.file_id
and t.parent_seq_id = l.tag_seq_id
)
, workflow as ( -- workflow 정보 찾기
select w.file_id, a.attr_value || '_' || a2.attr_value work_name 
from taglist w, ais0039 a, taglist t, ais0039 a2, ais0039 a3
where w.tag_name = 'WORKFLOW'
and a.prj_id = w.prj_id
and a.file_id = w.file_id
and a.tag_seq_id = w.tag_seq_id
and a.attr_name = 'NAME'
and t.prj_id = w.prj_id
and t.file_id = w.file_id
and t.parent_seq_id = w.tag_seq_id
and t.tag_name = 'TASKINSTANCE'
and a2.prj_id = t.prj_id
and a2.file_id = t.file_id
and a2.tag_seq_id = t.tag_seq_id
and a2.attr_name = 'NAME'
and a3.prj_id = t.prj_id
and a3.file_id = t.file_id
and a3.tag_seq_id = t.tag_seq_id
and a3.attr_name = 'TASKTYPE'
and a3.attr_value in ('Session')
)
, shortcut as ( -- 소스/타겟명 찾기
select t.file_id, t.tag_seq_id sql_id, tt.tag_attr_seq_id tbl_id
	 , tt.attr_value as tbl_nm, w.work_name || '_' || so.attr_value as obj_nm, so.tag_seq_id obj_id, so.attr_value
from taglist t, ais0039 so, ais0039 tp, ais0039 tt, workflow w
where t.tag_name = 'SHORTCUT'
and so.prj_id = t.prj_id
and so.file_id = t.file_id
and so.tag_seq_id = t.tag_seq_id
and so.attr_name = 'NAME' -- object
and tp.prj_id = t.prj_id
and tp.file_id = t.file_id
and tp.tag_seq_id = t.tag_seq_id
and tp.attr_name = 'OBJECTTYPE'
and tp.attr_value in ('SOURCE', 'TARGET')
and tt.prj_id = t.prj_id
and tt.file_id = t.file_id
and tt.tag_seq_id = t.tag_seq_id
and tt.attr_name = 'REFOBJECTNAME' -- table
and w.file_id = t.file_id
--order by t.tag_seq_id, so.tag_attr_seq_id, t.line_no, t.column_no
)
-- Last  LEVEL : object -> table
select tt.prj_id          prj_id
	 , stc.file_id         file_id
	 , stc.sql_id          sql_id
	 , stc.obj_id          tbl_id
	 , c.tag_attr_seq_id   col_id
	 , tt.prj_id          call_prj_id
	 , stc.file_id         call_file_id
	 , stc.sql_id          call_sql_id
	 , stc.tbl_id          call_tbl_id
	 , c.tag_attr_seq_id   call_col_id
	 , 0                   obj_id
	 , 0                   func_id
	 , '[owner_undefined]' owner_name
	 , stc.obj_nm          tbl_nm
	 , upper(stc.obj_nm)   caps_tbl_nm
	 , 'obj'               sql_obj_type
	 , c.attr_value        col_nm
	 , upper(c.attr_value) caps_col_nm
	 , 'N'                 call_value_yn
	 , c.attr_value        col_expr
	 , c.attr_value        col_nm_org
	 , upper(c.attr_value)   caps_col_nm_org
	 , 0                   call_obj_id
	 , 0                   call_func_id
	 , '[owner_undefined]' call_owner_name
	 , stc.tbl_nm          call_tbl_nm
	 , upper(stc.tbl_nm)   call_caps_tbl_nm
	 , 'tbl'               call_sql_obj_type
	 , c.attr_value        call_col_nm
	 , upper(c.attr_value) call_caps_col_nm
	 , 'N'                 call_col_value_yn
	 , ''                  call_col_expr
	 , c.attr_value        call_col_name_org
	 , upper(c.attr_value) call_caps_col_nm_org
	 , '[owner_undefined]' unique_owner_name
	 , '[owner_undefined]' call_unique_owner_name
	 , '[owner_undefined]' unique_owner_tgt_srv_id
	 , '[owner_undefined]' call_unique_owner_tgt_srv_id
	 , 1                   cond_mapping
	 , 2002                data_maker
	 , null                MAPPING_KIND
	 , ROW_NUMBER() OVER(order by c.line_no) col_order_no
	 , ROW_NUMBER() OVER(order by c.line_no) call_col_order_no
	 , ROW_NUMBER() OVER(order by c.line_no) adj_col_order_no
	 , ROW_NUMBER() OVER(order by c.line_no) call_adj_col_order_no
	 , '[owner_undefined]' as SYSTEM_BIZ_ID
     , '[owner_undefined]' as CALL_SYSTEM_BIZ_ID
from shortcut stc, taglist t, ais0039 tt, taglist ct, ais0039 c
where t.file_id = stc.file_id 
and t.tag_name = 'TARGET'
and tt.prj_id = t.prj_id
and tt.file_id = t.file_id
and tt.tag_seq_id = t.tag_seq_id
and tt.attr_name = 'NAME' -- target table
and tt.attr_value = stc.tbl_nm
and ct.file_id = t.file_id
and ct.parent_seq_id = t.tag_seq_id
and ct.tag_name = 'TARGETFIELD'
and c.prj_id = ct.prj_id
and c.file_id = ct.file_id
and c.tag_seq_id = ct.tag_seq_id
and c.attr_name = 'NAME'



INSERT INTO AIS0112 ( /* infomatica.mappingGroup-QT_DF_MST_TBLMP#4 */                                              
                    PRJ_ID,                                                                                              
                    FILE_ID,                                                                                             
                    SQL_ID,                                                                                              
                    TABLE_ID,                                                                                            
                    CALL_PRJ_ID,                                                                                         
                    CALL_FILE_ID,                                                                                        
                    CALL_SQL_ID,                                                                                         
                    CALL_TABLE_ID,                                                                                       
                    OBJ_ID,                                                                                              
                    FUNC_ID,                                                                                             
                    OWNER_NAME,                                                                                          
                    TABLE_NAME,                                                                                          
                    CAPS_TABLE_NAME,                                                                                     
                    SQL_OBJ_TYPE,                                                                                        
                    CALL_OBJ_ID,                                                                                         
                    CALL_FUNC_ID,                                                                                        
                    CALL_OWNER_NAME,                                                                                     
                    CALL_TABLE_NAME,                                                                                     
                    CALL_CAPS_TABLE_NAME,                                                                                
                    CALL_SQL_OBJ_TYPE,                                                                                   
                    UNIQUE_OWNER_NAME,                                                                                   
                    CALL_UNIQUE_OWNER_NAME,                                                                              
                    UNIQUE_OWNER_TGT_SRV_ID,                                                                             
                    CALL_UNIQUE_OWNER_TGT_SRV_ID,                                                                        
                    COND_MAPPING_BIT,                                                                                    
                    DATA_MAKER,                                                                                          
                    MAPPING_KIND,
                    SYSTEM_BIZ_ID                 ,
                    CALL_SYSTEM_BIZ_ID             )                                                                                       
SELECT DISTINCT                                                                          
          PRJ_ID                , FILE_ID                 , SQL_ID                       , TABLE_ID                      
        , CALL_PRJ_ID           , CALL_FILE_ID            , CALL_SQL_ID                  , CALL_TABLE_ID                 
        , OBJ_ID                , FUNC_ID                 , OWNER_NAME                   , TABLE_NAME                    
        , CAPS_TABLE_NAME       , SQL_OBJ_TYPE            , CALL_OBJ_ID                  , CALL_FUNC_ID                  
        , CALL_OWNER_NAME       , CALL_TABLE_NAME         , CALL_CAPS_TABLE_NAME         , CALL_SQL_OBJ_TYPE             
        , UNIQUE_OWNER_NAME     , CALL_UNIQUE_OWNER_NAME  , UNIQUE_OWNER_TGT_SRV_ID      , CALL_UNIQUE_OWNER_TGT_SRV_ID  
        , 2 as COND_MAPPING     , DATA_MAKER              , MAPPING_KIND
        , DA.SYSTEM_BIZ_ID                      AS SYSTEM_BIZ_ID               
        , DA.CALL_SYSTEM_BIZ_ID                 AS CALL_SYSTEM_BIZ_ID          
FROM AIS0113 DA                                                                                                          
WHERE DA.PRJ_ID = ##{{prj_id}}                                                                                                      
AND DA.DATA_MAKER IN (2000,2001,2002)                                                            
AND NOT EXISTS ( SELECT /*+ HASH_AJ  */ 'X'                                                                              
                   FROM AIS0112 A112                                                                                     
                  WHERE A112.PRJ_ID                               = DA.PRJ_ID                                            
                    AND A112.FILE_ID                              = DA.FILE_ID                                           
                    AND A112.SQL_ID                               = DA.SQL_ID                                            
                    AND A112.TABLE_ID                             = DA.TABLE_ID                                          
                    AND A112.CALL_PRJ_ID                          = DA.CALL_PRJ_ID                                       
                    AND A112.CALL_FILE_ID                         = DA.CALL_FILE_ID                                      
                    AND A112.CALL_SQL_ID                          = DA.CALL_SQL_ID                                       
                    AND A112.CALL_TABLE_ID                        = DA.CALL_TABLE_ID                                     
                   ) 