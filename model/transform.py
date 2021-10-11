import ocrmypdf
import os
import pdf2image
import pdfrw, pdfrw.toreportlab
import PIL.Image, PIL.ImageOps, PIL.ImageColor
import reportlab
import sys
import tempfile
import time

project_root = os.getcwd() # where the app is started from; NOT where the controller file is and NOT where this file is
# print(project_root)

option = sys.argv[1]
# print(option)
filename = sys.argv[2]
# print(filename)
text_color = PIL.ImageColor.getcolor(sys.argv[3], "RGB")
# print(text_color)
language_code = sys.argv[4]
# print(language_code)

print("accepting input pdf")
time.sleep(0.1) # sleep for 0.1s. need these small time delays after each print because of issue with spawn grouping the print outputs without the delays
inpdf = f"{project_root}/data/{filename}_in.pdf"
print("accepted input pdf")
time.sleep(0.1)

i = 1

if option == "dim":
	# initialization
	read_inpdf = pdfrw.PdfReader(inpdf)
	inpdf_pages = read_inpdf.pages
	inpdf_num_pages = len(read_inpdf.pages)

	# create reportlab canvas
	print("creating canvas")
	time.sleep(0.1)
	outpdf = f"{project_root}/data/{filename}_out.pdf"
	canvas = reportlab.pdfgen.canvas.Canvas(outpdf, pagesize=reportlab.lib.pagesizes.A4)
	canvas.setTitle("")
	print("created canvas")
	time.sleep(0.1)

	# set up input pdf to transfer to reportlab canvas
	print("setting up input pdf to transfer to canvas")
	time.sleep(0.1)
	inpdf_pages = [pdfrw.buildxobj.pagexobj(page) for page in inpdf_pages[0:inpdf_num_pages]]

	# put input pdf pages onto canvas and add a dimmer layer on top of each page
	print("dimming pages")
	time.sleep(0.1)
	for page in inpdf_pages:
		canvas.doForm(pdfrw.toreportlab.makerl(canvas, page))
		canvas.setFillColor(reportlab.lib.colors.Color(0.43, 0.43, 0.43, alpha=0.5))
		canvas.rect(0, 0, 8.26*reportlab.lib.units.inch, 11.69*reportlab.lib.units.inch, fill=1)
		canvas.showPage()
		print("done 1 page") if i==1 else print(f"done {i} pages")
		time.sleep(0.1)
		i += 1
	print(f"dimmed all pages ({i-1})")
	time.sleep(0.1)

	# save output pdf
	print("creating output pdf")
	time.sleep(0.1)
	canvas.save()
	print("created output pdf")
	time.sleep(0.1)
else:
	with tempfile.TemporaryDirectory() as temp_dir: # gets auto-deleted when context (or process) is exited
		# convert input pdf pages to images
		print("loading...")
		time.sleep(0.1)
		images = pdf2image.convert_from_path(inpdf, dpi=300, output_folder=temp_dir) # pdf −> list of pil image objects

		# convert images to dark mode
		print("applying dark mode")
		time.sleep(0.1)
		for image in images:
			image = PIL.ImageOps.grayscale(image)
			image = PIL.ImageOps.invert(image)
			image = PIL.ImageOps.colorize(image, black=(43,43,43), white=text_color)
			image.save(f"{temp_dir}/image_{str(i)}.jpg", format="JPEG", progressive=True, optimize=True)
			image.close() # release memory (method seems to be bugged; memory leaks from this loop (till this python spawn process exits))
			print("done 1 page") if i==1 else print(f"done {i} pages")
			time.sleep(0.1)
			i += 1
		print(f"dark moded all pages ({i-1})")
		time.sleep(0.1)

		# combine images into pdf
		print("saving...")
		time.sleep(0.1)
		image_1 = PIL.Image.open(f"{temp_dir}/image_1.jpg")
		images = []
		for num in range(2, i):
			images.append(PIL.Image.open(f"{temp_dir}/image_{str(num)}.jpg"))
		if option == "no_ocr_dark" or option == "no_ocr_dark_retain_img_colors":
			image_1.save(f"{project_root}/data/{filename}_temp.pdf", format="PDF", append_images=images, save_all=True, title="", resolution=300) # resolution affects page dimensions, not file size. match resolution with dpi
		elif option == "ocr_dark":
			image_1.save(f"{temp_dir}/temp.pdf", format="PDF", append_images=images, save_all=True, title="", resolution=300) # resolution affects page dimensions, not file size. match resolution with dpi

			# ocr: fork a child process to perform the ocr so that the application will survive if ocrmypdf.ocr fails
			print("forking process to perform ocr")
			time.sleep(0.1)
			pid = os.fork()
			if pid > 0: # parent process
				# wait for child process to end
				os.waitpid(pid, 0)
				print("child process exited with exit status 0")
				time.sleep(0.1)
			elif pid == 0: # child process
				# ocr the pdf and create output pdf
				print("child process performing ocr (this might take a while)...")
				time.sleep(0.1)
				ocrmypdf.ocr(f"{temp_dir}/temp.pdf", f"{project_root}/data/{filename}_out.pdf", force_ocr=True, output_type="pdf", language=language_code)
				print("done ocr")
				time.sleep(0.1)
				print("created output pdf")
				time.sleep(0.1)
				os._exit(0) # exit child process
