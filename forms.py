from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired,FileField
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField,RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp 


 
class SearchForm(FlaskForm):
    search = StringField('Search',validators=[DataRequired()])
    # select=SelectField('类别',choices=[('video','视频'),('img','图片'), ('music','音乐'), ('story','小说'), ('all','所有'), ('none','') ],default='none' )
   
    # submit = SubmitField('确定',  render_kw={'class': 'btn btn-sm btn-outline-secondary'})
    submit = SubmitField('确定' )

class FilterForm(FlaskForm):
    media_type = RadioField('选择媒体类型',
                            choices=[('video', '视频'), ('img', '图片'),
                                     ('story', '文字'),('music','音乐')],render_kw={'class_': 'form-check-inline'})
    submit = SubmitField('确定' )
class SortForm(FlaskForm):
    media_type = RadioField('排序方式',
                            choices=[('ctime', '创建时间'), ('size', '大小'),
                                     ('name', '文件名'),('path','路径'),('utime','添加时间')],render_kw={'class': 'form-check-inline'})
    submit = SubmitField('确定' )
     
class TagForm(FlaskForm):
    tag = StringField('Tag', validators=[DataRequired()])
    submit = SubmitField('确定' )

class AddDirForm(FlaskForm):
    addpath = StringField('添加路径逗号分隔'  )
    isdelpath = StringField('检查删除路径逗号分隔' )
    submit = SubmitField('确定' )

class UpFile(FlaskForm):
   
    file=FileField(label='文件',validators=[FileRequired()],render_kw={'multiple':True} )
    submit=SubmitField( '提交' )