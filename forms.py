from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired,FileField
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp 


 
class SearchForm(FlaskForm):
    search = StringField('Search')
    select=SelectField('类别',choices=[('video','视频'),('img','图片'), ('music','音乐'), ('story','小说'), ('all','所有'), ('none','') ],default='none' )
    most_data=BooleanField(label='最多')
    dir=BooleanField(label='目录')
    like=BooleanField(label='喜欢')
    # submit = SubmitField('确定',  render_kw={'class': 'btn btn-sm btn-outline-secondary'})
    submit = SubmitField('确定' )

class TagForm(FlaskForm):
    tag = StringField('Tag', validators=[DataRequired()])
    submit = SubmitField('确定' )

class AddDirForm(FlaskForm):
    path = StringField('路径逗号分隔', validators=[DataRequired()])
    submit = SubmitField('确定' )

class UpFile(FlaskForm):
   
    file=FileField(label='文件',validators=[FileRequired()],render_kw={'multiple':True} )
    submit=SubmitField( '提交' )