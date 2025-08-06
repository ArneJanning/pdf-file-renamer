from typing import Optional
from pydantic import BaseModel, Field


class BibliographicInfo(BaseModel):
    """Model for bibliographic information extracted from PDF."""
    
    author: Optional[str] = Field(
        None, 
        description="Primary author(s) of the publication. Use 'et al.' for multiple authors if needed."
    )
    author_last: Optional[str] = Field(
        None,
        description="Last name only of the primary author."
    )
    editor: Optional[str] = Field(
        None, 
        description="Editor(s) of the publication if no author is present."
    )
    editor_last: Optional[str] = Field(
        None,
        description="Last name only of the primary editor."
    )
    year: Optional[str] = Field(
        None, 
        description="Year of publication (YYYY format preferred)."
    )
    title: str = Field(
        ..., 
        description="Title of the publication."
    )
    
    @property
    def author_or_editor(self) -> str:
        """Return author if available, otherwise editor, otherwise 'Unknown'."""
        if self.author:
            return self.author
        elif self.editor:
            return f"{self.editor} (Ed.)"
        else:
            return "Unknown"
    
    @property
    def author_or_editor_last(self) -> str:
        """Return last name of author if available, otherwise editor, otherwise 'Unknown'."""
        if self.author_last:
            return self.author_last
        elif self.editor_last:
            return self.editor_last
        else:
            return "Unknown"
    
    def format_filename(self, template: str) -> str:
        """
        Format filename based on template.
        
        Args:
            template: Template string with placeholders
            
        Returns:
            Formatted filename
        """
        # Clean up values for filename
        author_or_editor = self._clean_for_filename(self.author_or_editor)
        author_or_editor_last = self._clean_for_filename(self.author_or_editor_last)
        year = self._clean_for_filename(self.year or "Unknown Year")
        title = self._clean_for_filename(self.title)
        author = self._clean_for_filename(self.author or "")
        author_last = self._clean_for_filename(self.author_last or "")
        editor = self._clean_for_filename(self.editor or "")
        editor_last = self._clean_for_filename(self.editor_last or "")
        
        # Replace placeholders
        filename = template.format(
            author_or_editor=author_or_editor,
            author_or_editor_last=author_or_editor_last,
            author=author,
            author_last=author_last,
            editor=editor,
            editor_last=editor_last,
            year=year,
            title=title
        )
        
        return filename
    
    @staticmethod
    def _clean_for_filename(text: str) -> str:
        """Clean text to be safe for filenames."""
        # Remove or replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            text = text.replace(char, '')
        
        # Replace multiple spaces with single space
        text = ' '.join(text.split())
        
        # Limit length to avoid filesystem issues
        max_length = 200
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + '...'
        
        return text.strip()


class ScreenshotInfo(BaseModel):
    """Model for information extracted from screenshots."""
    
    application: Optional[str] = Field(
        None,
        description="The application or software visible in the screenshot."
    )
    date: Optional[str] = Field(
        None,
        description="Date visible in the screenshot (YYYY-MM-DD format preferred)."
    )
    time: Optional[str] = Field(
        None,
        description="Time visible in the screenshot (HH:MM format preferred)."
    )
    content_type: Optional[str] = Field(
        None,
        description="Type of content (e.g., 'email', 'chat', 'document', 'website', 'error', 'settings')."
    )
    main_subject: str = Field(
        ...,
        description="Main subject or topic of the screenshot content."
    )
    
    def format_filename(self, template: str) -> str:
        """
        Format filename based on template.
        
        Args:
            template: Template string with placeholders
            
        Returns:
            Formatted filename
        """
        # Clean up values for filename
        application = self._clean_for_filename(self.application or "Unknown")
        date = self._clean_for_filename(self.date or "Unknown-Date")
        time = self._clean_for_filename(self.time or "")
        content_type = self._clean_for_filename(self.content_type or "Screenshot")
        main_subject = self._clean_for_filename(self.main_subject)
        
        # Create datetime string if both date and time are available
        datetime = f"{date} {time}".strip() if date != "Unknown-Date" and time else date
        
        # Replace placeholders
        filename = template.format(
            application=application,
            date=date,
            time=time,
            datetime=datetime,
            content_type=content_type,
            main_subject=main_subject
        )
        
        return filename
    
    @staticmethod
    def _clean_for_filename(text: str) -> str:
        """Clean text to be safe for filenames."""
        # Remove or replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            text = text.replace(char, '')
        
        # Replace multiple spaces with single space
        text = ' '.join(text.split())
        
        # Limit length to avoid filesystem issues
        max_length = 200
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + '...'
        
        return text.strip()